export const drawGoogleGauges = (data) => {
  google.charts.load('current', { packages: ['gauge'] });
  google.charts.setOnLoadCallback(() => {
    data.forEach(item => {
      const container = document.getElementById(`gauge-${item.id}`);
      if (container) {

        container.style.border = '1px solid #ccc';
        container.style.boxShadow =  '0 0 3px white';
        container.style.margin = '5px';
        container.style.borderRadius = '10px';
        container.style.padding = '10px';
        container.style.display = 'inline-block';

        // Extract the part of signalname before the underscore
        const signalLabel = item.signalname.split('_')[0];

        // Create the data table
        const chartData = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          [signalLabel, item.value] // Use extracted label here
        ]);

        // Define gauge options
        const options = {
          min: 0,
          max: 100,
          redFrom: 50,
          redTo: 100,
          yellowFrom: 30,
          yellowTo: 50,
          greenFrom: 6,
          greenTo: 30,
          grayFrom: 0,
          grayTo: 6,
          minorTicks: 5,
        };

        // Create and draw the gauge
        const chart = new google.visualization.Gauge(container);
        chart.draw(chartData, options);

        // Optionally resize the chart after drawing
        // google.visualization.events.addListener(chart, 'ready', () => {
        //   google.visualization.events.addListener(chart, 'resize', () => {
        //     chart.draw(chartData, options);
        //   });
        // });
      }
    });
  });
};
