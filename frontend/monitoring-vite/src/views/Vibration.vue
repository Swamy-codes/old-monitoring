<template>
  <div class="Vibration">
    <div class="container mx-auto">
      <h3 class="text-xl text-center text-blue-500 font-bold">
        Selected Machine: {{ selectedMachineName }}
      </h3>
      <br />
      <!-- <p>Active Link: {{ props.componentName['__name']}}</p> -->
    </div>
    <div class="grid grid-rows-4 grid-cols-5 grid-flow-col gap-4">
      <div class="LiveVibrationData  row-span-3 col-span-1">
        <ul class="grid grid-cols-1 gap-4">
          <li class="bg-blue-50 shadow  flex flex-row items-center" v-for="item in vibrationData" :key="item.id || 0">
            <div class="ml-5" v-html="getSvgContent(item.status)"></div>
            <div class="flex flex-col p-3">
              <p><b>{{ getHumanReadableSignalName(item.signalname) }}</b></p>
              <p :style="{ color: statusStore.getStatusColor(item.status) }"><b >Status :
                  {{ item.status }}</b></p>
            </div>

            <p class="ml-auto p-5 text-xl " :style="{ color: statusStore.getStatusColor(item.status) }"><b>
                {{ item.value }} mm/sec</b> </p>

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
            <div>
            </div>
          </div>
        </div>
        <PlotlyChart :key="chartKey" :data="filterStore.chartData[chartKey]" :layout="chartLayout"
          class="bg-pink-100" />
      </div>
    </div>
  </div>

</template>

<script setup>

import { ref, onMounted, onUnmounted, watch, toRefs, computed } from "vue";
import { useVibrationFilterStore } from '../store/baseFilterStore'
import { storeToRefs } from 'pinia';
import { useStatusStore } from '../store/statusStore.js'
// import motor from '../assets/Design/motor.svg'
// import spindle from '../assets/Design/Spindle.svg'
import PlotlyChart from '../components/PlotlyChart.vue'
import { defineProps } from 'vue';


const props = defineProps({
  selectedMachineName: String,
  componentName: String,
  ist_updatedate: String,
})

const selectedComponent = String(props.componentName['__name'])
const vibrationData = ref([])
const ws = ref(null);
const statusStore = useStatusStore()
const svgTemplateMotor = ref('')
const svgTemplateSpindle = ref('')
const filterStore = useVibrationFilterStore()
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
      title: 'Vibration- mm/sec',
      autorange: true,
    },
  };
});


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

const fetchSvgContent = async () => {
  try {
    // Fetch SVGs
    const responseMotor = await fetch(motor);
    const responseSpindle = await fetch(spindle);

    // Check if the responses are OK
    if (!responseMotor.ok) {
      throw new Error("Failed to fetch SVG Content for motor");
    }
    if (!responseSpindle.ok) {
      throw new Error("Failed to fetch SVG Content for spindle");
    }

    // Set the SVG content
    svgTemplateMotor.value = await responseMotor.text();
    svgTemplateSpindle.value = await responseSpindle.text();

    // Log the SVG content
    console.log("SVG Motor:", svgTemplateMotor.value);
    console.log("SVG Spindle:", svgTemplateSpindle.value);
  } catch (error) {
    console.error('Error fetching SVG:', error);
    svgTemplateMotor.value = '';
    svgTemplateSpindle.value = '';
  }
}

const getSvgContent = (status) => {

  const color = statusStore.getStatusColor(status);
  console.log("Col", color)
  // svgTemplate.value= svgTemplate.value.replace(`fill="statusColors"`, `fill="${color}"`); console.log("svg2",svgTemplate.value)
  // return svgTemplate.value 
  return svgTemplateSpindle.value.replace(`fill="statusColors"`, `fill="${color}"`);
}

const applyFilters = () => {
  filterStore.applyDate(props.selectedMachineName, selectedComponent, selectedSignalName.value,);
  console.log("info2", props.selectedMachineName, selectedComponent, selectedSignalName.value,)
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

  ws.value.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      vibrationData.value = data.Livedata;
      console.log("liveData123", vibrationData.value);
      fetchSvgContent();
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
  connectWebSocket()
  console.log("Temp Component mounted");
  console.log("temp elected Machine Name:", props.selectedMachineName);
  console.log("TempS elected Component:", props.selectedComponent);
  filterStore.fetchSignalName(props.selectedMachineName, selectedComponent)
  filterStore.updateGranularity()
  // filterStore.updateChartData
})
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
    () => selectedGranularity.value],
  () => {
    console.log("Watched temp props changed");
    connectWebSocket(props.selectedMachineName, selectedComponent)
    filterStore.fetchSignalName(props.selectedMachineName, selectedComponent),
      filterStore.updateGranularity(),
      applyFilters()
  },

  { immediate: true }
)


</script>