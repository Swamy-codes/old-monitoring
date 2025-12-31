import { defineStore } from 'pinia'
import axios from 'axios';
import Plotly from 'plotly.js-dist';

// export const useBaseFilterStore =  defineStore('baseFilter' , {
export const useBaseFilterStore = (name) => defineStore((name), {
  state: () => ({
    selectedFirstDate: null,
    selectedSecondDate: null,
    granularity: [],
    selectedGranularity: null,
    signalName: [],
    selectedSignalName: '',
    dateRange: false,
    graphData: [],
    chartData: [],
    signalDict: {},
    signalDictReverse: {}
  }),

  getters: {
    dateRangeButtonText: (state) => {
      // console.log("ki")
      return state.dateRange ? 'Reset' : 'Add Range for Date?'
    }
  },

  actions: {

    updateSignalDict(signalDict = {}) {
      this.signalDict = {
        Coolant_Pressure: "Coolant Pressure",
        Lub_Pressure: "Lubrication Pressure",
        Hydraulic_Pressure: "Hydraulic Pressure",
        Tailstock_Pressure: "Tailstock Pressure",
        Chuck_Pressure: "Chuck Pressure",

        Coolant_Level: "Coolant Level",
        Hydraulic_Level: "Hydraulic Level",

        Spin_Front_X: "Vibration-Spindle Front X Axis",
        Spin_Front_Y: "Vibration-Spindle Front Y Axis",
        Spin_Rear_X: "Vibration-Spindle Rear X Axis",
        Spin_Rear_Y: "Vibration-Spindle Rear Y Axis",

        Mtr_Front_X: "Vibration-Motor Front X Axis",
        Mtr_Front_Y: "Vibration-Motor Front Y Axis",
        Mtr_Rear_X: "Vibration-Motor Rear X Axis",
        Mtr_Rear_Y: "Vibration-Motor Rear Y Axis",

        Hyd_Mtr_Temp: "Hydraulic Motor Temperature",
        Spn_Back_Temp: "Spindle Back Temperature",
        Spn_Front_Temp: "Spindle Front Temperature",
        Axis_Z_Temp: "Servo Motor Temperature-Z",
        Spn_Mtr_Back_Temp: "Spindle Motor Back Temperature",
        Axis_X_Temp: "Servo Motor Temperature-X",
        Spn_Mtr_Front_Temp: "Spindle Motor Front Temperature",

        Machine_Energy: "Machine Energy",
        Spindle_Energy: "Spindle Energy"
      };
      this.signalDictReverse = Object.fromEntries(
        Object.entries(this.signalDict).map(([key, value]) => [value, key])
      );
    },


    async fetchSignalName(selectedMachineName, selectedComponent) {
      try {
        if (!selectedMachineName || !selectedComponent) {
          throw new Error("Selected machine name or component is missing.");
        }

        this.updateSignalDict();
        const url = `http://127.0.0.1:8000/signalName/${selectedMachineName}/${selectedComponent}`
        console.log('Fetching URL:', url);
        const response = await fetch(url)

        console.log("selectedcompo1", selectedComponent, selectedMachineName)
        console.log("signalNameresponse", response)

        if (!response.ok) {
          throw new Error("Failed to fetch signal name from backend")
        }
        const jsonData = await response.json();
        // console.log(typeof(jsonData))
        
        // const mappedSignalNames = jsonData.map(item => {
        //   const originalName = item.selected_signal_name.trim();
        //   const mappedName = this.signalDict[originalName] || originalName;
        //   return mappedName;
        // });
        // this.signalName = mappedSignalNames;
        this.signalName = jsonData 
       
      //    console.log("signalNameData", this.signalName)
      console.log("signalName", signalName)

      } catch (error) {
        console.error("Error fetching signal names:", error);
      }


     
      // catch (error) {
      //   console.error("Errr fetchin signal data", error)
      // }

    },

    toggleDateRange() {
      this.dateRange = !this.dateRange

      if (!this.dateRange) {
        this.selectedSecondDate = null; // Clear the second date if range is disabled
      }
    },

    // addGranularity(values) {
    //   this.granularity.push(...values); // Use spread to add multiple values
    // },
    updateGranularity() {
      this.granularity = ['hour', 'minute', 'second']

    },
    getTimePattern(granularity) {
      // granularity = granularity.toLowerCase()
      console.log("case", granularity)
      switch (granularity.toLowerCase()) {
        case 'hour':
          return /\d{2}:\d{2}/; // e.g., 12:34
        case 'minute':
          return /\d{2}:\d{2}/; // e.g., 12:34
        case 'second':
          return /\d{2}:\d{2}:\d{2}/; // e.g., 12:34:56
        default:
          return /\d{2}:\d{2}:\d{2}/; // Default pattern if granularity is unknown
      }
    },
    async applyDate(selectedMachineName, selectedComponent, selectedSignalName) {
      try {
        const rawSignalName = this.signalDictReverse[selectedSignalName] || selectedSignalName;
        const params = {
          signal_name: rawSignalName,
          start_date: this.selectedFirstDate,
          end_date: this.selectedSecondDate,
          granularity_str: this.selectedGranularity,
          // multiplr_dates
        };
        // console.log("selectedSignalNamegdv", selectedSignalName)

        Object.keys(params).forEach(key => params[key] === undefined && delete params[key]);

        const url = `http://127.0.0.1:8000/machineData/${selectedMachineName}/${selectedComponent}`
        console.log("Reqapp url", url)
        console.log("reqapp params", params)

        const response = await axios.get(url, { params })
        console.log('gdvDatafetched:', response.data)

        this.graphData = response.data
        // this.graphData.value = response.data
        console.log("graphdate", this.graphData)
        this.updateChartData(selectedMachineName, selectedComponent, selectedSignalName, this.selectedGranularity)
      } catch (error) {
        console.error("error fetching store data", error)
      }
    },
    updateChartData(selectedMachineName, selectedComponent, selectedSignalName, selectedGranularity) {
      if (!this.graphData || typeof this.graphData !== 'object') {
        console.error("Graph data is not object", typeof this.graphData)

        return
      }

      const graphDataValue = this.graphData.machineData
      if (!Array.isArray(graphDataValue)) {
        console.error("graphData.machineData is not an array", typeof graphDataValue);
        return;
      }
      console.log("checkgdv", this.graphData.machineData.length)
      console.log("gdv", graphDataValue.length)

      const len = Object.keys(graphDataValue).length
      const y_array = []
      const x_array = []
      const timePattern = this.getTimePattern(selectedGranularity);

      for (let i = 0; i < len; i++) {
        y_array.push(graphDataValue[i].value)

        const datetime = graphDataValue[i][selectedGranularity];
        const timeMatch = datetime.match(timePattern);

        if (timeMatch && timeMatch.length > 0) {
          x_array.push(timeMatch[0]);
          console.log("gdv x_array.timematch", timeMatch[0]);
        } else {
          console.warn("No match found for datetime:", datetime);
        }
      }

      // console.log("gdvx", graphDataValue[i].hour)
      //     const timeMatch = graphDataValue[i].hour.match(/\d{2}:\d{2}:\d{2}.\d{1}/)
      //     if (timeMatch && timeMatch.length > 0) {
      //       x_array.push(timeMatch[0]);
      //       console.log("gdv x_array.timematch", timeMatch[0]);
      //   } else {
      //       console.warn("No match found for ist_updatedate:", graphDataValue[i].hour);
      //   }



      console.log('gdv y_array', y_array[0]);
      console.log('gdv x_array type', typeof x_array)
      console.log('gdv x_array type[0]', typeof x_array[0])
      console.log("gdv x_array", x_array[0])

      console.log(`info: ${selectedMachineName}-${selectedComponent}-${selectedSignalName}`)


      this.chartData[`${selectedMachineName}-${selectedComponent}-${selectedSignalName}`] = [{
        x: x_array,
        y: y_array,
        type: 'scatter',
        mode: 'lines+markers',
        marker: { color: 'blue' },
        line: { shape: 'linear' },
        // name: `${selectedMachineName}-${selectedComponent}-${selectedSignalName}`,
      }];
      console.log("Chart data updated:", this.chartData);
      // this.downloadData(selectedMachineName, selectedComponent, selectedSignalName, this.chartData)
    },

    async downloadData(chartData, selectedMachineName, selectedComponent, selectedSignalName) {
      const selectedGranularity = this.selectedGranularity;
      // let csvContent = "data:text/csv;charset=utf-8,"; 
      let csvContent = "";
      const machineName = `Machine Name: ${selectedMachineName}`
      const dataType = `${selectedComponent} Data -  ${selectedSignalName} Plot`
      const dateRow1 = `Date Range Start: ${this.selectedFirstDate}`;
      const dateRow2 = `Date Range End: ${this.selectedSecondDate}`;
      csvContent += `${machineName}\n${dataType}\n${dateRow1}\n${dateRow2}\n\n`;

      Object.keys(chartData).forEach(key => {
        const data = chartData[key][0]; // Assuming each key has an array with a single object
        const headers = `Time (${selectedGranularity}),${selectedSignalName}`;
        const rows = data.x.map((x, index) => `${x},${data.y[index]}`);

        // Add headers and rows to csvContent
        // csvContent += headers + "\n" + rows.join("\n");
        csvContent += `${headers}\n${rows.join("\n")}\n\n`;
      });
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = URL.createObjectURL(blob)

      const a = document.createElement('a');
      a.href = url;
      a.download = `${selectedMachineName}-${selectedComponent}-${selectedSignalName}.csv`;
      document.body.appendChild(a); // Append to body to work in Firefox
      a.click();
      document.body.removeChild(a); // Remove after download
      URL.revokeObjectURL(url);
    },



  }
})

export const useTemperatureFilterStore = useBaseFilterStore('temperatureFilter');
export const useLevelFilterStore = useBaseFilterStore('levelFilter');
export const usePressureFilterStore = useBaseFilterStore('pressureFilter');
export const useEnergyFilterStore = useBaseFilterStore('energyFilter');
export const useVibrationFilterStore = useBaseFilterStore('vibrationFilter');


// MCV-450-Temperature-Spn_Mtr_Front_Temp MCV-450-Temperature-Spn_Mtr_Front_Temp