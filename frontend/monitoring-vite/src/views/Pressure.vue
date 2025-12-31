<template>
  <div class="pressure">
    <div class="container mx-auto">
      <h3 class="text-xl text-center text-blue-500 font-bold">
        Selected Machine: {{ selectedMachineName }}
      </h3>
      <br />
      <!-- <p>Active Link: {{ props.componentName['__name'] }}</p> -->
    </div>
      <div class="flex justify-center">
        <ul class="LivePressData flex flex-row ">
          <li class=" flex flex-col items-center  m-3" v-for="item in pressureData" :key="item.id || 0">
            <div :id="'gauge-' + item.id" class="gauge-chart"></div>
            <div class="flex flex-col items-center justify-center">
              <p class=" m-auto text-center"><b>{{ getHumanReadableSignalName(item.signalname) }}</b></p>
              <p :style="{ color: statusStore.getStatusColor(item.status)}">
                <b>{{ item.status }}</b>
              </p>
            </div>
            <p class="m-auto  text-xl" :style="{ color: statusStore.getStatusColor(item.status) }">
              <b>{{ item.value.toFixed(2) }} Bar</b>
            </p>
          </li>
        </ul>
      </div>

      <!-- Date and Signal Selector -->
      <div class="row-span-4 col-span-4">
        <div class="flex flex-wrap">
          <!-- Signal Selector -->
          <div class="signalName flex-2">
            <div class="rounded p-1 bg-gray-200 border-solid border-2 border-sky-100">
              <select :disabled="filterStore.signalName.length === 0" v-model="selectedSignalName" 
                      @change="filterStore.fetchSignalName" class="w-full p-3">
                <option value="" disabled>Select Signal</option>
                <option v-for="Signal_name in filterStore.signalName" :key="Signal_name" :value="Signal_name">
                  {{ Signal_name}}
                </option>
              </select>
            </div>
          </div>

          <!-- Date Range Selection -->
          <div class="date flex-1">
            <div class="p-2">
              <input type="date" v-model="selectedFirstDate" class="rounded p-2 border border-gray-500 shadow-sm mr-5">
              <input v-if="dateRange" type="date" v-model="selectedSecondDate" class="rounded p-2 border border-gray-500 shadow-sm mr-5">
              <button @click="toggleDateRange" class="rounded p-2 mr-5 bg-third text-white hover:bg-blue-500">
                {{ dateRangeButtonText }}
              </button>
Group Data By
              <select class="rounded p-2 mr-5 bg-gray-100 border border-solid border-gray-500 shadow-sm"
             :disabled="filterStore.granularity.length === 0" 
            v-model="selectedGranularity" 
            @change="handleGranularityChange">
              <option value="" disabled>Group Data by</option>
              <option v-for="(granularityElements, index) in filterStore.granularity" 
              :key="index" 
              :value="granularityElements">
              {{granularityElements}}
              </option>
            </select>

              <button class="p-2 px-10 mr-5 bg-green-600 text-white hover:bg-green-700 rounded" @click="applyFilters">
                Apply
              </button>
              <button
               class="p-2 px-10 mr-5 bg-sky-600 text-white hover:bg-sky-700 rounded"
                @click="handleDownloadCSV">Download CSV
                </button></div>
              
          </div>
        </div>

        <!-- Plotly Chart -->
        <PlotlyChart :key="chartKey" :data="filterStore.chartData[chartKey]" :layout="chartLayout" class="bg-pink-100" />
      </div>
  </div>
  
</template>

<script setup>
import { drawGoogleGauges } from '../components/Charts/googleCharts/pressureGauge.js';
import PlotlyChart from '../components/PlotlyChart.vue';
import { ref, onMounted, onUnmounted, watch, computed } from "vue";
import { usePressureFilterStore } from '../store/baseFilterStore'
import { storeToRefs } from 'pinia';
import { useStatusStore } from '../store/statusStore.js';
import { defineProps } from 'vue';


const props = defineProps({
  selectedMachineName: String,
  componentName: String,
  ist_updatedate: String
});

const selectedComponent = String(props.componentName['__name']);
const pressureData = ref([]); 
const ws = ref(null);
const statusStore = useStatusStore();
const filterStore = usePressureFilterStore();
const { selectedFirstDate, selectedSecondDate, dateRange, dateRangeButtonText, 
selectedSignalName, granularity, selectedGranularity } = storeToRefs(filterStore);
const { toggleDateRange, applyDate, fetchSignalName, downloadData } = filterStore;

const chartLayout = computed(() => ({
  title: `${selectedSignalName.value} Graph - Grouped by ${selectedGranularity.value} Data`,
  plot_bgcolor: "#F3FAFE",
    paper_bgcolor:"#F3FAFE",
    xaxis: {
    title: 'Timestamp',
    type: 'category',
  },
  yaxis: {
    title: 'Pressure- Bar',
    autorange: true,
  },
}));

const chartKey = computed(() => `${props.selectedMachineName}-${selectedComponent}-${selectedSignalName.value}`);
const handleDownloadCSV = () =>{
  console.log("handleDownloadData")
  filterStore.downloadData(
    chartData.value,
    props.selectedMachineName,
    selectedComponent,
    selectedSignalName.value
  )
}
const applyFilters = () => {
  filterStore.applyDate(props.selectedMachineName, selectedComponent, selectedSignalName.value);
  console.log("graph Chart Data after applyDate:", filterStore.chartData);
};


const connectWebSocket = () => {
  if (ws.value) {
    ws.value.close();  
  }
  const machineName = encodeURIComponent(props.selectedMachineName || '');
  const selectedComponent = props.componentName["__name"] || '';
  // Construct the WebSocket URL
  const url = `ws://127.0.0.1:8000/ws/${machineName}/${selectedComponent}`;
  

  // Initialize the WebSocket connection
  ws.value = new WebSocket(url);
  console.log("wsss", url)

  ws.value.onmessage = (event) => {
  try {
    const data = JSON.parse(event.data);
    pressureData.value = data.Livedata;
    console.log("liveData123", pressureData.value);
    drawGoogleGauges(pressureData.value); 
  } catch (e) {
    console.error('Error parsing WebSocket message:', e);
  }
};


  ws.value.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  ws.value.onclose = () => {
    console.log('WebSocket connection closed');
  };
};

const handleGranularityChange=()=>{
  filterStore.selectedGranularity = selectedGranularity.value
}
const getHumanReadableSignalName = (signalName) => {
  return filterStore.signalDict[signalName] || signalName;
};


onMounted(() => {
  // connectWebSocket(props.selectedMachineName, selectedComponent);
  connectWebSocket()
  filterStore.fetchSignalName(props.selectedMachineName, selectedComponent);
  filterStore.updateGranularity()
});

onUnmounted(() => {
  if (ws.value) {
    ws.value.close(); 
    ws.value = null;
  }
});

watch(
  [
    () => props.selectedMachineName,
    () => selectedComponent,
    () => selectedSignalName.value,
    ()=>selectedGranularity.value
  ],
  () => {
    // connectWebSocket(MachineName, selectedComponent);
    connectWebSocket()
    filterStore.fetchSignalName(props.selectedMachineName, selectedComponent);
    filterStore.updateGranularity(),
    applyFilters();
  },
  { immediate: true }
);
</script>

<style scoped>
.gauge-chart {
  width: 200px; 
  height: 200px; 
}
</style>