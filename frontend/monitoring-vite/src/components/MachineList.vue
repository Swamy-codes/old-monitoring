<template>
    <div>
        <div class = "p-5 bg-gray-700 machineList">
            <ul class="hover:bg-white">
                <li v-for="machine in useMachineStore.machines" :key="machine.id">
                    <button type="button" @click = "useMachineStore.selectedMachine(machine.id)">{{machine.name}}</button>
                </li>
            </ul>
        </div>
        
    </div>
</template>


<script setup>

import {machineStore} from '../store/machineStore'

const useMachineStore = machineStore()
useMachineStore.fetchMachines()

// machines= useMachineStore.machines,
// selectedMachine= useMachineStore.selectedMachine


</script>
