<template>
  <div class="energy">
    <div class="container mx-auto">
      <h3 class="text-xl text-center text-blue-500 font-bold">
        Selected Machine: {{ selectedMachineName }}
      </h3>
      <br />
      <!-- <p>Active Link: {{ props.componentName['__name'] }}</p> -->
    </div>

    <!-- <div class="flex justify-center"> -->
    <div class="flex justify-center">
      <ul class="LiveEnegyData flex flex-row ">
        <li class="flex flex-col items-center  m-3" v-for="item in energyData" :key="item.id || 0">
          <div :id="'gauge-' + item.id" class="gauge-chart"></div>
          <div class="flex flex-col">
            <p class="m-auto"><b>{{ getHumanReadableSignalName(item.signalname) }}</b></p>
            <p :style="{ color: statusStore.getStatusColor(item.status) }" class="text-center">
              <b>{{ item.status }}</b>
            </p>

          </div>
          <p class="m-auto  text-xl" :style="{ color: statusStore.getStatusColor(item.status) }">
            <b>{{ item.value.toFixed(2) }} kWh</b>
          </p>
        </li>
      </ul>
    </div>

    <!-- Signnal name Dropdowns and Date Picker -->
    <div class="row-span-4 col-span-4 ...">
      <div class=" flex flex-wrap">
        <div class="signalName flex-2">
          <div class="rounded p-1 bg-gray-200 border-solid border-2 border-sky-100">
            <select :disabled="filterStore.signalName.length == 0" v-model="selectedSignalName"
              @change="filterStore.fetchSignalName" class="w-full p-3">
              <option value="" disabled>Select Signal</option>
              <option v-for="Signal_name in filterStore.signalName" :key="Signal_name" :value="Signal_name">
                {{ Signal_name }}
              </option>
            </select>
          </div>
        </div>

        <div class=" date flex-1">
          <div class="p-2">
            <input type="date" v-model="selectedFirstDate"
              class="rounded mr-5 date-picker p-2 border border-solid border-gray-500 shadow-sm">
            <input v-if="dateRange" type="date" v-model="selectedSecondDate"
              class="rounded mr-5 date-picker p-2 border border-solid border-gray-500 shadow-sm">
            <button @click="toggleDateRange" class="rounded p-2 mr-5 bg-third text-white hover:bg-blue-500">
              {{ dateRangeButtonText }}</button>
            Group Data By
            <select class="rounded p-2 mr-5 bg-gray-100 border border-solid border-gray-500 shadow-sm"
              :disabled="filterStore.granularity.length === 0" v-model="selectedGranularity"
              @change="handleGranularityChange">
              <option value="" disabled>Group Data by</option>
              <option v-for="(granularityElements, index) in filterStore.granularity" :key="index"
                :value="granularityElements">
                {{ granularityElements }}
              </option>
            </select>

            <button class="p-2 px-10 mr-5 bg-green-600 text-white hover:bg-green-700 rounded" @click="applyFilters">
              Apply </button>

            <button class="p-2 px-10 mr-5 bg-sky-600 text-white hover:bg-sky-700 rounded"
              @click="handleDownloadCSV">Download CSV
            </button>
          </div>

        </div>
      </div>
      <PlotlyChart :key="chartKey" :data="filterStore.chartData[chartKey]" :layout="chartLayout" class="bg-pink-100" />

    </div>
  </div>
</template>

<script setup>

import { ref, onMounted, onUnmounted, nextTick, watch, computed, toRefs } from 'vue';
import { useEnergyFilterStore } from '../store/baseFilterStore'
import { useStatusStore } from '../store/statusStore.js'
import PlotlyChart from '../components/PlotlyChart.vue'
import { updateGauges } from '../components/Charts/eCharts/EnergyChart.js';

import { defineProps } from 'vue';


const props = defineProps({
  selectedMachineName: String,
  componentName: String,
  ist_updatedate: String,
})

const selectedComponent = String(props.componentName['__name'])
const energyData = ref([])
const ws = ref(null);
const statusStore = useStatusStore()
const filterStore = useEnergyFilterStore()
const { selectedFirstDate, selectedSecondDate, dateRange, dateRangeButtonText,
  graphData, chartData, signalName, selectedSignalName, granularity, selectedGranularity } = toRefs(filterStore)
const { toggleDateRange, applyDate, fetchSignalName, downloadData } = filterStore

const chartLayout = computed(() => {
  return {
    title: `${selectedSignalName.value} Graph - Grouped by ${selectedGranularity.value} Data`,
    plot_bgcolor: "#F3FAFE",
    paper_bgcolor: "#F3FAFE",
    xaxis: {
      title: 'Timestamp',
      type: 'category',
    },
    yaxis: {
      title: 'Energy- kWh',
      autorange: true,
    },
  };
});

console.log(`sig-name,${props.selectedMachineName}-${selectedComponent}-${selectedSignalName.value}`)

console.log("selected details", energyData.value)

const chartKey = computed(() => {
  return `${props.selectedMachineName}-${selectedComponent}-${selectedSignalName.value}`;
});

const handleDownloadCSV = () => {
  console.log("handleDownloadData")
  filterStore.downloadData(
    chartData.value,
    props.selectedMachineName,
    selectedComponent,
    selectedSignalName.value
  )
}

const applyFilters = () => {
  filterStore.applyDate(props.selectedMachineName, selectedComponent, selectedSignalName.value,);
  console.log("Chart Data after applyDate:", filterStore.chartData);
};

const handleGranularityChange = () => {
  filterStore.selectedGranularity = selectedGranularity.value
}

const connectWebSocket = () => {
  if (ws.value) {
    ws.value.close();
  }
  const machineName = encodeURIComponent(props.selectedMachineName || '');
  const selectedComponent = props.componentName["__name"] || '';
  // Construct the WebSocket URL
  const url = `ws://127.0.0.1:8000/ws/${machineName}/${selectedComponent}`;
  ws.value = new WebSocket(url);

  ws.value.onmessage = async (event) => {
    try {
      const data = JSON.parse(event.data);
      energyData.value = data.Livedata;
      console.log("energyData", energyData);
      await nextTick();
      updateGauges(energyData.value);
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
const getHumanReadableSignalName = (signalName) => {
  return filterStore.signalDict[signalName] || signalName;
};


onMounted(() => {
  connectWebSocket(props.selectedMachineName, selectedComponent);
  filterStore.fetchSignalName(props.selectedMachineName, selectedComponent);
  filterStore.updateGranularity()
});
onUnmounted(() => {
  if (ws.value) {
    ws.value.close();
  }
});

watch(
  [
    () => props.selectedMachineName,
    () => selectedComponent,
    () => selectedSignalName.value,
    () => selectedGranularity.value
  ],
  async () => {
    console.log("Watched energy props changed");
    nextTick();
    connectWebSocket(props.selectedMachineName, selectedComponent);
    filterStore.fetchSignalName(props.selectedMachineName, selectedComponent);
    filterStore.updateGranularity(),
      applyFilters();
  },
  { immediate: true }
);



</script>

<style scoped>
.gauge-chart {
  width: 400px;
  height: 200px;
}
</style>