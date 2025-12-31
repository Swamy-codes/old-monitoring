<template>
  <div class="Level">
    <div class="container mx-auto">
      <h3 class="text-xl text-center text-blue-500 font-bold">
        Selected Machine: {{ selectedMachineName }}
      </h3>
      <br />
    <!-- <p>Active Link: {{ props.componentName['__name']}}</p> -->
    </div>
    <div class="flex justify-center"> 
      <ul class="levelDataBlock flex flex-row ">
        <li class="flex flex-col items-center m-10" v-for="item in levelData" :key="item.id">
          <waterBubbleChart
            :options="{
              ...bubbleOptions,
              data: item.value / 100,
              txt: item.value !== undefined && !isNaN(item.value)
                ? `${parseFloat(item.value).toFixed(1)}%`
                : 'Invalid value'
            }"
          />
          <p>
            <b>{{ getHumanReadableSignalName(item.signalname) }}</b>
          </p>
          <p :style="{ color: statusStore.getStatusColor(item.status) }">
            <b>{{ item.status }}</b>
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
                    {{ Signal_name}}
                </option>
            </select>
        </div>
    </div>

    <div class=" date flex-1">
        <div class="p-2">
            <input type="date" v-model="selectedFirstDate" class="rounded mr-5 date-picker p-2 border border-solid border-gray-500 shadow-sm">
            <input v-if="dateRange" type="date" v-model="selectedSecondDate" class="rounded mr-5 date-picker p-2 border border-solid border-gray-500 shadow-sm">
            <button  @click="toggleDateRange"
            class="rounded p-2 mr-5 bg-third text-white hover:bg-blue-500">
            {{ dateRangeButtonText }}</button>

            Group Data By
            <select class="rounded p-2 mr-5 bg-gray-100 border border-solid border-gray-500 shadow-sm"
             :disabled="filterStore.granularity.length === 0" 
            v-model="selectedGranularity" 
            @change="handleGranularityChange">LL
              <option value="" disabled>Group Data by</option>
              <option v-for="(granularityElements, index) in filterStore.granularity" 
              :key="index" 
              :value="granularityElements">
              {{granularityElements}}
              </option>
            </select>
            
            <button class="p-2 mr-5 bg-green-600 text-white hover:bg-green-700 rounded" 
            @click="applyFilters">Apply</button>
            <button
               class="p-2 px-10 mr-5 bg-sky-600 text-white hover:bg-sky-700 rounded"
                @click="handleDownloadCSV">Download CSV
                </button></div>
              <div>
        </div>
    </div>
</div>
    <PlotlyChart :key="chartKey" :data="filterStore.chartData[chartKey]" :layout="chartLayout" class="bg-pink-100"/>
  </div>
 </div>
  
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed, toRefs } from "vue";
import waterBubbleChart from "../components/waterBubbleChart.vue"
import { useLevelFilterStore} from '../store/baseFilterStore'
import { useStatusStore } from "../store/statusStore.js";
import PlotlyChart from '../components/PlotlyChart.vue'
import { defineProps } from 'vue';


const levelData = ref([]);
const ws = ref(null);
const statusStore = useStatusStore();
const filterStore = useLevelFilterStore()
const { selectedFirstDate, selectedSecondDate, dateRange, dateRangeButtonText, graphData, 
chartData, signalName, selectedSignalName, granularity, selectedGranularity } = toRefs(filterStore)
const {toggleDateRange, applyDate, fetchSignalName, downloadData} = filterStore


const props = defineProps({
  selectedMachineName:String,
  componentName: String,
  ist_updatedate: String,
})
const bubbleOptions = {
  radius: 60,
  data: 1,
  txt: "NaN",
};
const selectedComponent = String(props.componentName['__name'])
console.log("sig-nameLevel", selectedSignalName.value )
const chartLayout = computed(() => {
  return {
    title: `${selectedSignalName.value} Graph - Grouped by ${selectedGranularity.value} Data`,
    plot_bgcolor: "#F3FAFE",
    paper_bgcolor:"#F3FAFE",
    xaxis: {
      title: 'Timestamp',
      type: 'category',
    },
    yaxis: {
      title: 'Liter %',
      autorange: true,
    },
  };
});


console.log("Level selected details", `${props.selectedMachineName}-${selectedComponent}-${filterStore.selectedSignalName}`)

const chartKey = computed(() => {
  return `${props.selectedMachineName}-${selectedComponent}-${selectedSignalName.value}`;
});

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
  console.log("applyFilters called");
  console.log("Selected First Date:", selectedFirstDate.value);
  console.log("Selected Second Date:", selectedSecondDate.value);
  console.log("Selected Machine Name:", props.selectedMachineName);
  console.log("Selected Component:", selectedComponent);
  console.log("Selected Signal Name:", selectedSignalName.value);
  filterStore.applyDate(props.selectedMachineName, selectedComponent, selectedSignalName.value,);
};

const handleGranularityChange=()=>{
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
      levelData.value = data.Livedata; 
      console.log("leveldata", levelData);
     
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
  console.log("Level Component mounted");
  console.log("Level Selected Machine Name:", props.selectedMachineName);
  console.log("Level Selected Component:", props.selectedComponent);
  filterStore.fetchSignalName(props.selectedMachineName, selectedComponent)
  filterStore.updateGranularity()
});
onUnmounted(() => {
  if (ws.value) {
    ws.value.close();
  }
});

watch(
  [
  ()=> props.selectedMachineName, 
  ()=>selectedComponent, 
  ()=>selectedSignalName.value,
  ()=>selectedGranularity.value
  ],
  ()=>{
    console.log("Watched Level props changed");
    connectWebSocket(props.selectedMachineName, selectedComponent);
    filterStore.fetchSignalName(props.selectedMachineName, selectedComponent), 
    filterStore.updateGranularity(),
  applyFilters()
  },
   {immediate:true})

</script>