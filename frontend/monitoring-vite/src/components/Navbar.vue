
<script setup>
// import {useCounterStore} from '../store/counterStore'
import cmtiLogo from '../assets/logo/cmtiLogo.svg'
import niamtLogo from '../assets/logo/niamtLogo.svg'

</script>

<template> 
    <header >
        
        <div class="bg-primary shadow-xl h-16 flex justify-between items-center">
            <!-- <div class="bg-pink-200 storeCounterPinia">{{storeCounter.countnew}}</div> -->
        <router-link :to="{name:'defaultLayout'}">
            <span class=" ml-5 flex items-stretch justify-center">
                <div class="m-1 content-around cmtiLogoimg"><img :src="cmtiLogo"/> </div>
                <div class="m-1 content-around niamtLogo"><img :src="niamtLogo"/></div>  
            </span>
        </router-link>
        <!-- //:to="{name:'about'}" -->
        <div class ="mr-5 flex items-center gap-5">
            <router-link  class="inline-block px-2 text-gray-200 hover:text-white"> 
                About
            </router-link>
            <router-link  class="inline-block px-2 text-gray-200  hover:text-white"> 
                Blog
            </router-link>
            <!-- :to ="{name:'logout'}" -->
            <router-link >
              <div class=" h-10 bg-gradient-to-r from-blue-800 to-indigo-800 
              rounded-md border border-indigo-600
              hover:from-blue-700 hover:to-indigo-700
              flex justify-center items-center">
          <button @click="toggleLogin()" class="m-3 rounded-md text-sm text-gray-200 hover:text-white">
            Logout
          </button>
        </div>
            </router-link>
            
        </div>
        </div>

    </header>
</template>
