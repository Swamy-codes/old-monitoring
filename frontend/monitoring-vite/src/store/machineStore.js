// give an emplty aray fro data na dcomputed data
// actions - fetch data from  mongodb- use axios t get api endpoint
    // computation an fetched data


// import {defineStore} from 'pinia'
// import axios from 'axios'

// export const machineStore = defineStore({
//     id: 'machine',

//     state:()=>({
//         machines: [],
//         selectedMachine :null,
//         machineData: {},

        
//     }),

//     actions: {
//         // machine list - name / id  is given/generated in vue 
//         async fetchMachines(){
//             try{
//                 const response = await axios.get('api_endpoint/machines')
//                 this.machines = response.data
//             }
//             catch(error) {
//                 console.error("Error fetchinf machines,", error)
//             }
//         },
//         //  particular  machine data correcponds to value and ststus s per limit
//         async fetchMachineData(machineID){
//             try {
//                 const response = await axios.get(`http://your-api-endpoint/machines/${machineID}/data`);
//                 this.machineData = response.data;
//               } 
//               catch (error) {
//                 console.error('Error fetching machine data:', error);
//               }
//         },


//         selectedMachine(machine) {
//             this.selectedMachine = machine
//             this.fetchMachineData(machine.id)
//         },


//     },

//     getters:{
//         machineAttributes:(state) =>state.machineData.attributes || [],
//     }
        

    
// })