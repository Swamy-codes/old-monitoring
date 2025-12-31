<template>
    <div>
        <Navbar />
        <main>
            <div class="bg-gradient-to-b from-blue-100 to-gray-100">
                <SubModules />
                <div v-if="!store.activeLink">
                    <Home />
                </div>
                <router-view />
            </div>
        </main>
    </div>
</template>

<script setup>
import { useSubModulesStore } from '../store/subModulesStore';
import Navbar from '../components/Navbar.vue';
import SubModules from '../components/SubModules.vue';
import Home from '../views/Home.vue';

const store = useSubModulesStore();
</script>
