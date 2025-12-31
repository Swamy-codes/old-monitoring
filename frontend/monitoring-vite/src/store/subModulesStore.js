import { defineStore } from 'pinia';
import Temperature from '../views/Temperature.vue';
import Level from '../views/Level.vue';
import Pressure from '../views/Pressure.vue';
import Vibration from '../views/Vibration.vue';
import Energy from '../views/Energy.vue';

export const useSubModulesStore = defineStore('subModulesStore', {
    state: () => ({
        notificationMessage: '',
        notificationTypeClass: '',
        notificationTimeout: null,

        machineName: [],
        selectedMachineName: '',
        activeLink: '',
        links: [
            "Temperature Monitoring",
            "Energy Monitoring",
            "Level Indicator Monitoring",
            "Pressure Monitoring",
            "Vibration Monitoring"
        ],
        componentMap: {
            "Temperature Monitoring": Temperature,
            "Energy Monitoring": Energy,
            "Level Indicator Monitoring": Level,
            "Pressure Monitoring": Pressure,
            "Vibration Monitoring": Vibration
        }
    }),
    actions: {
        setActiveLink(link) {
            this.activeLink = link;
            this.fetchNotification();
        },
        setSelectedMachineName(name) {
            this.selectedMachineName = name;
            this.fetchNotification();
        },
        showNotification(message, type) {
            this.notificationMessage = message;
            this.notificationTypeClass = type;

            if (this.notificationTimeout) {
                clearTimeout(this.notificationTimeout);
            }

            this.notificationTimeout = setTimeout(() => {
                this.clearNotification();
            }, 3000);
        },
        clearNotification() {
            this.notificationMessage = '';
            this.notificationTypeClass = '';
            if (this.notificationTimeout) {
                clearTimeout(this.notificationTimeout);
                this.notificationTimeout = null;
            }
        },
        async fetchMachineList() {
            try {
                const response = await fetch('http://127.0.0.1:8000/machineName');
                if (!response.ok) {
                    throw new Error("Failed to fetch machine name from backend");
                }
                const jsonData = await response.json();
                this.machineName = jsonData || [];
            } catch (error) {
                this.showNotification('Error fetching machine names.', 'notification-error');
                console.error("Error fetching data", error);
            }
        },
        async fetchNotification() {
            if (!this.selectedMachineName || !this.activeLink) {
                // Display a more specific notification based on what is missing
                if (!this.selectedMachineName) {
                    this.showNotification('Please select a Machine name.', 'notification-error');
                } 
                if (!this.activeLink) {
                    this.showNotification('Please select a Parameter.', 'notification-error');
                }
                return;
            }

            try {
                const response = await fetch('http://127.0.0.1:8000/machineName', {
                    params: {
                        machineName: this.selectedMachineName,
                        link: this.activeLink
                    }
                });

                if (!response.ok) {
                    throw new Error("Failed to fetch notification data");
                }

                const data = await response.json();
                this.showNotification('Data fetched successfully.', 'notification-success');
                // Process the data if needed
            } catch (error) {
                this.showNotification('Error fetching data. Please try again later.', 'notification-error');
                console.error("Error fetching data", error);
            }
        }
    }
});
