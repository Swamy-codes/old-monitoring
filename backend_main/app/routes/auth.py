from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from asyncpg import Pool
from fastapi.security import OAuth2PasswordRequestForm
from database.postgres import get_postgres_pool_1  

router = APIRouter(prefix="/auth")

# Secret and JWT settings
SECRET_KEY = "your_jwt_secret"  # 🔐 Change this to a strong, secure key!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str


class User(BaseModel):
    id: int
    username: str
    role: str

# Password verification
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Token creation
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Token decoding (optional)
def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# Main login route (POST /auth/login)
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Pool = Depends(get_postgres_pool_1)):
    async with db.acquire() as conn:
        print(f"Login attempt for: {form_data.username}")

        result = await conn.fetchrow("SELECT * FROM auth WHERE username = $1", form_data.username)
        if not result:
            print("❌ User not found")
            raise HTTPException(status_code=400, detail="Invalid username or password")

        print(f"✅ User found: {result['username']}")
        password_match = verify_password(form_data.password, result["password"])
        if not password_match:
            print("❌ Incorrect password")
            raise HTTPException(status_code=400, detail="Invalid username or password")

        role = result["role"]
        if role.lower() not in ["admin", "supervisor","operator"]:
            print("❌ Unauthorized role")
            raise HTTPException(status_code=403, detail="Unauthorized role")

        # Create JWT token
        token_data = {"sub": result["username"], "role": result["role"]}
        token = create_access_token(token_data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

        print("✅ Login successful")
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": result["role"]
        }
