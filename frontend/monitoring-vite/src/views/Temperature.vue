<template>
  <div class="tempee">
    <div class="container mx-auto">
      <h1 class="text-xl text-center text-blue-500 font-bold">
        Selected Machine: {{ selectedMachineName }}
      </h1>
      <!-- {{ temperatureData.value(0) }} -->
      <br />
      <!-- <p>Active Link: {{ props.componentName['__name']}}</p> -->
    </div>
    <div class="grid grid-rows-4 grid-cols-5 grid-flow-col gap-4">
      <button @click="clicked" class="LiveTempData row-span-3 col-span-1">
        <ul class="grid grid-cols-1 gap-4">
          <li
            class="bg-blue-50 shadow flex flex-row items-center"
            v-for="item in temperatureData"
            :key="item.id || 0"
          >
            <div v-html="getSvgContent(item.status)"></div>
            <div class="flex flex-col">
              <p>
                <b>{{ getHumanReadableSignalName(item.signalname) }}</b>
              </p>
              <p :style="{ color: statusStore.getStatusColor(item.status) }">
                <b>Status : {{ item.status }}</b>
              </p>
            </div>

            <p
              class="ml-auto p-5 text-xl"
              :style="{ color: statusStore.getStatusColor(item.status) }"
            >
              <b> {{ item.value }} °C</b>
            </p>
          </li>
        </ul>
      </button>

      <!-- Signnal name Dropdowns and Date Picker -->

      <div class="row-span-4 col-span-4 ...">
        <div class="flex flex-wrap">
          <div class="signalName flex-2">
            <div
              class="rounded p-1 bg-gray-200 border-solid border-2 border-sky-100"
            >
              <select
                :disabled="filterStore.signalName.length == 0"
                v-model="selectedSignalName"
                @change="filterStore.fetchSignalName"
                class="w-full p-3"
              >
                <option value="" disabled>Select Signal</option>
                <option
                  v-for="Signal_name in filterStore.signalName"
                                   :key="Signal_name.selected_signal_name"
                  :value="Signal_name.selected_signal_name"
                >
                  {{ Signal_name.selected_signal_name }}
                </option>
              </select>
            </div>
          </div>

          <div class="date flex-1">
            <div class="p-2">
              <input
                type="date"
                v-model="selectedFirstDate"
                class="rounded mr-5 date-picker p-2 border border-solid border-gray-500 shadow-sm"
              />
              <input
                v-if="dateRange"
                type="date"
                v-model="selectedSecondDate"
                class="rounded mr-5 date-picker p-2 border border-solid border-gray-500 shadow-sm"
              />
              <button
                @click="toggleDateRange"
                class="rounded p-2 mr-5 bg-third text-white hover:bg-blue-500"
              >
                {{ dateRangeButtonText }}
              </button>
              Group Data By
              <select
                class="rounded p-2 mr-5 bg-gray-100 border border-solid border-gray-500 shadow-sm"
                :disabled="filterStore.granularity.length === 0"
                v-model="selectedGranularity"
                @change="handleGranularityChange"
              >
                <option value="" disabled selected>Group Data by</option>
                <option
                  v-for="(
                    granularityElements, index
                  ) in filterStore.granularity"
                  :key="index"
                  :value="granularityElements"
                >
                  {{ granularityElements }}
                </option>
              </select>

              <button
                class="p-2 px-10 mr-5 bg-green-600 text-white hover:bg-green-700 rounded"
                @click="applyFilters"
              >
                Apply
              </button>
              <button
                class="p-2 px-10 mr-5 bg-sky-600 text-white hover:bg-sky-700 rounded"
                @click="handleDownloadCSV"
              >
                Download CSV
              </button>
              <div></div>
            </div>
          </div>
        </div>
        <PlotlyChart
          :key="chartKey"
          :data="filterStore.chartData[chartKey]"
          :layout="chartLayout"
          class="bg-pink-100"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, toRefs, computed } from "vue";
import { useTemperatureFilterStore } from "../store/baseFilterStore";
import { useStatusStore } from "../store/statusStore.js";
import tempDesign from "../assets/Design/thermometer.svg";
import PlotlyChart from "../components/PlotlyChart.vue";
import { defineProps } from "vue";

const props = defineProps({
  selectedMachineName: String,
  componentName: String,
  ist_updatedate: String,
});

const selectedComponent = String(props.componentName["__name"]);
const temperatureData = ref([]);
const statusStore = useStatusStore();
const svgTemplate = ref("");
const filterStore = useTemperatureFilterStore();
const ws = ref(null);

const {
  selectedFirstDate,
  selectedSecondDate,
  dateRange,
  dateRangeButtonText,
  graphData,
  chartData,
  signalName,
  selectedSignalName,
  granularity,
  selectedGranularity,
} = toRefs(filterStore);
const { toggleDateRange, applyDate, fetchSignalName, downloadData } = filterStore;

const chartLayout = computed(() => {
  return {
    title: `${selectedSignalName.value} Graph - Grouped by ${selectedGranularity.value} Data`,
    plot_bgcolor: "#F3FAFE",
    paper_bgcolor: "#F3FAFE",
    xaxis: {
      title: "Timestamp",
      type: "category",
    },
    yaxis: {
      title: "Temperature (°C)",
      autorange: true,
    },
  };
});

const chartKey = computed(() => {
  return `${props.selectedMachineName}-${selectedComponent}-${selectedSignalName.value}`;
});

const clicked = () => {
  console.log("Button clicked");
};

const fetchSvgContent = async () => {
  try {
    const response = await fetch(tempDesign);
    if (!response.ok) {
      throw new Error("Failed to fetch SVG Content");
    }
    svgTemplate.value = await response.text();
    // console.log("svg",svgTemplate.value)
  } catch (error) {
    console.error("Error fetching SVG", error);
    svgTemplate.value = "";
  }
};

const getSvgContent = (status) => {
  const color = statusStore.getStatusColor(status);
  return svgTemplate.value.replace(`fill="statusColors"`, `fill="${color}"`);
};

const handleDownloadCSV = () => {
  filterStore.downloadData(
    chartData.value,
    props.selectedMachineName,
    selectedComponent,
    selectedSignalName.value
  );
};

const applyFilters = () => {
  filterStore.applyDate(
    props.selectedMachineName,
    selectedComponent,
    selectedSignalName.value
  );
};

const handleGranularityChange = () => {
  filterStore.selectedGranularity = selectedGranularity.value;
};

const connectWebSocket = () => {
  if (ws.value) {
    ws.value.close();
    ws.value = null;
  }
  const machineName = encodeURIComponent(props.selectedMachineName || "");
  const selectedComponent = props.componentName["__name"] || "";
  const url = `ws://127.0.0.1:8000/ws/${machineName}/${selectedComponent}`;
  console.log("Connecting to WebSocket URL:", url);

  // Initialize the WebSocket connection
  ws.value = new WebSocket(url);

  ws.value.onopen = () => {
    console.log("WebSocket connection opened");
  };

  ws.value.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      temperatureData.value = data.Livedata || [];
      // console.log("liveData123", temperatureData.value);
      fetchSvgContent();
    } catch (e) {
      console.error("Error parsing WebSocket message:", e);
    }
  };

  ws.value.onerror = (event) => {
    console.error("WebSocket error:", event);
    if (event.message) {
      console.error("Error message:", event.message);
    }
    if (event.reason) {
      console.error("Error reason:", event.reason);
    }
  };

  ws.value.onclose = () => {
    console.log("WebSocket connection closed");
  };
};

const getHumanReadableSignalName = (signalName) => {
  return filterStore.signalDict[signalName] || signalName;
};

onMounted(() => {
  connectWebSocket();
  filterStore.fetchSignalName(props.selectedMachineName, selectedComponent),
    filterStore.updateGranularity(),
    clicked();
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
    () => selectedGranularity.value,
  ],
  () => {
    connectWebSocket();
    filterStore.fetchSignalName(props.selectedMachineName, selectedComponent),
      filterStore.updateGranularity(),
      clicked(),
      applyFilters();
  },

  { immediate: true }
);
</script>
