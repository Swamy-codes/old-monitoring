from fastapi import APIRouter, HTTPException, Path, Request
from pydantic import BaseModel
from database.postgres import get_postgres_pool_1
import traceback

router = APIRouter(prefix="/machine-issue", tags=["Machine Issues check"])

class MachineIssueCreate(BaseModel):
    machine_name: str
    operator: str
    issue_related: str | None = None
    issue_text: str | None = None

class MachineIssueUpdateStatus(BaseModel):
    status: str

@router.put("/{issue_id}/status")
async def update_issue_status(issue_id: int = Path(...), status_update: MachineIssueUpdateStatus = None, request: Request = None):
    try:
        pool = await get_postgres_pool_1(request)
        query = """
            UPDATE machine_issues
            SET status = $1
            WHERE id = $2
            RETURNING id, status;
        """
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, status_update.status, issue_id)

        if not row:
            raise HTTPException(status_code=404, detail="Issue not found")

        return {"status": "success", "data": dict(row)}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/")
async def create_machine_issue(issue: MachineIssueCreate, request: Request):
    print("📥 Received POST /machine-issues request")
    print(f"➡ Payload: {issue.dict()}")

    try:
        pool = await get_postgres_pool_1(request)  # Pass the request object
        print("✅ PostgreSQL pool acquired")

        query = """
            INSERT INTO machine_issues (machine_name, operator, issue_related, issue_text)
            VALUES ($1, $2, $3, $4)
            RETURNING id;
        """
        print(f"📝 Executing query: {query.strip()}")

        async with pool.acquire() as conn:
            print("📡 Connection acquired")
            new_id = await conn.fetchval(
                query,
                issue.machine_name,
                issue.operator,
                issue.issue_related,
                issue.issue_text
            )

        print(f"✅ Insert successful, new ID = {new_id}")
        return {"status": "success", "id": new_id}

    except Exception as e:
        print("❌ ERROR inserting machine issue")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_all_machine_issues(request: Request):
    print("📥 Received GET /machine-issues request")

    try:
        pool = await get_postgres_pool_1(request)
        print("✅ PostgreSQL pool acquired")

        query = """
            SELECT id, machine_name, operator, issue_related, issue_text,status
            FROM machine_issues
            ORDER BY id DESC;
        """
        print(f"📝 Executing query: {query.strip()}")

        async with pool.acquire() as conn:
            print("📡 Connection acquired")
            rows = await conn.fetch(query)

        results = [dict(row) for row in rows]
        print(f"✅ Retrieved {len(results)} issues")
        return {"status": "success", "data": results}

    except Exception as e:
        print("❌ ERROR fetching machine issues")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/null-status")
async def get_null_status_machine_issues(request: Request):
    print("📥 Received GET /machine-issues/null-status request")

    try:
        pool = await get_postgres_pool_1(request)
        print("✅ PostgreSQL pool acquired")

        query = """
            SELECT id, machine_name, operator, issue_related, issue_text, status
            FROM machine_issues
            WHERE status IS NULL
            ORDER BY id DESC;
        """
        print(f"📝 Executing query: {query.strip()}")

        async with pool.acquire() as conn:
            print("📡 Connection acquired")
            rows = await conn.fetch(query)

        results = [dict(row) for row in rows]
        print(f"✅ Retrieved {len(results)} null-status issues")
        return {"status": "success", "data": results}

    except Exception as e:
        print("❌ ERROR fetching null-status machine issues")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))