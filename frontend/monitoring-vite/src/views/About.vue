
 <template>
  <div class="about"> 
    <h1>Temperature Data</h1>
    <ul v-if="temperatureData.length = 2" >
      <li v-for="item in temperatureData" :key="item.id">
        <p>L1 Name: {{ item.l1name }}</p>
        <p>Signal Name: {{ item.signalname }}</p>
        <p>Value: {{ item.value }}</p>
        <p>Status: {{ item.status }}</p>
        <p>Update Date: {{ item.updatedate }}</p>
      </li>
    </ul>
    <p v-else>No temperature data available.</p> 
  </div>
</template>

<script>
export default {
  data() {
    return {
      temperatureData: [],
    };
  },
  created() {
    this.fetchTemperatureData();
  },
  methods: {
    async fetchTemperatureData() {
      try {
        const response = await fetch('http://localhost:8000/api/temperature-data?limit=2');
        if (!response.ok) {
          throw new Error('Failed to fetch temperature data');
        }
        const jsonData = await response.json();
        this.temperatureData = jsonData.data;
        console.log('Fetched temperature data:', this.temperatureData); // Log fetched data
      } catch (error) {
        console.error('Error fetching temperature data:', error);
        // Optionally handle error display or retries
      }
    },
  },
};
</script> 