<template>
 <div ref="plotElement"></div>
</template>



<script setup>
import {ref, watchEffect} from 'vue'
import Plotly from 'plotly.js-dist'

// props
const props = defineProps({
    data:Array,
    layout:Object
})

// References
const plotElement = ref(null)

// Render function
const renderChart=()=>{
    if(plotElement.value){
        Plotly.newPlot(plotElement.value, props.data, props.layout)
    }
}


watchEffect(() =>{
    console.log('Plotly data:', props.data); // Debugging line
  console.log('Plotly layout:', props.layout); // Debugging line
    renderChart()
})
</script>