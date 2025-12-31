<template>
    <div>
        <div v-if="store.notificationMessage" :class="['notification', store.notificationTypeClass]">
            <span>{{ store.notificationMessage }}</span>
            <span class="close" @click="store.clearNotification">&times;</span>
        </div>

        <div class="subModule bg-blue-100 flex justify-between items-center">
            <div class="p-2 w-1/5 bg-blue-200 border-solid border-2 border-sky-100">
                <select :disabled="store.machineName.length == 0" v-model="store.selectedMachineName" @change="store.fetchNotification"
                    class="w-full p-3">
                    <option value="" disabled>Select Machine</option>
                    <option v-for="Machine_name in store.machineName" :key="Machine_name.selected_machine_name || NaN">{{ Machine_name.selected_machine_name }}</option>
                </select>
            </div>

            <div class="w-4/5 flex items-center gap-20">
                <div class="w-full grid grid-cols-5 divide-x">
                    <div v-for="link in store.links" :key="link">
                        <button
                            class="w-full p-5 bg-gray-50 hover:bg-blue-300 inline-block px-2 text-blue-400 hover:text-blue-900 flex items-center justify-center active:bg-blue-200 focus:outline-none focus:border focus:border-blue-400"
                            :class="{ 'focus': store.activeLink === link }"
                            @click="store.setActiveLink(link)">
                            {{ link }}
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div v-for="link in store.links" :key="link + '-detail'">
            <div v-if="store.activeLink === link">
                <!-- {{ link }}  -->
                <!-- {{store.componentMap[link]}} -->
                <!-- {{store.selectedMachineName}} -->
                <component
                    :is="store.componentMap[link]" 
                    :selected-machine-name="store.selectedMachineName"
                    :component-name="store.componentMap[link]" />
            </div>
            <!-- <div v-else>None</div> -->
        </div>
    </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useSubModulesStore } from '../store/subModulesStore';

const store = useSubModulesStore();

onMounted(store.fetchMachineList);
</script>

<style scoped>
.notification {
  position: fixed;
  top: 130px;
  right: 20px;
  padding: 15px;
  border-radius: 5px;
  font-size: 16px;
  font-weight: bold;
  z-index: 1000;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transition: opacity 0.5s ease;
  opacity: 1;
  transition: opacity 0.5s ease;
}
.notification.fade-out {
  opacity: 0;
}

.notification-success {
  background-color: #4CAF50;
  color: white;
}

.notification-error {
  background-color: #f44336;
  color: white;
}

/* .notification-warning {
  background-color: #FFC107;
  color: black;
} */

.notification-info {
  background-color: #2196F3;
  color: white;
}

.notification .close {
  cursor: pointer;
  font-size: 20px;
  font-weight: bold;
}

.notification .close:hover {
  color: black;
}
</style>
