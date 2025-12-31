import {defineStore} from 'pinia'


export  const useStatusStore =  defineStore('status', {
    state:()=>({
        statusColors:{
            Normal: 'green',
            Mtr_Normal: 'green',
            Spn_Normal: 'green',
            High: 'red',
            Mtr_High: 'red',
            Spn_High: 'red',
            Low: 'orange',
            Emergency: '#EFB719',
            Switched_Off: 'gray',
            Tolerance: '#CC7722',
            Spn_Tolerance: '#CC7722',
            Mtr_Tolerance: '#CC7722'
        }
    }),
    getters:{
        getStatusColor: (state) =>(status) =>state.statusColors[status] || '#71C5E8'
    }
})