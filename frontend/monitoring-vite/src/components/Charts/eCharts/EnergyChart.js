import * as echarts from 'echarts';

export const getGaugeOption = (item) => ({
    series: [
        {
            type: 'gauge',
            center: ['50%', '60%'],
            startAngle: 200,
            endAngle: -20,
            min: 0,
            max: 100,
            splitNumber: 10,
            itemStyle: {
                color: (valueObj) => {
                    const value = valueObj.value; // Access the numeric value if `value` is an object
                    //   console.log(`Value received for color: ${value}`); 
                    //   if (value === 0) return 'red';
                    //   if (value > 0 && value <= 10) return 'green'; 
                    //   if (value >= 11 && value <= 15) return 'yellow';
                    //   if (value > 15) return 'orange';
                    //   return 'red'; // Fallback
                    // },
                    if (value >= 0 && value <= 1) {
                        return 'lightcoral';
                    } else if (value > 1 && value <= 10) {
                        return 'green';
                    } else if (value > 10 && value <= 15) {
                        return 'yellow';
                    } else if (value > 15) {
                        return 'red';
                    } else {
                        return 'lightblue'
                    }
                }
            },

            progress: {
                show: true,
                width: 30,
            },
            pointer: {
                show: true,
            },
            axisLine: {
                lineStyle: {
                    width: 30,
                },
            },
            axisTick: {
                distance: -45,
                splitNumber: 5,
                lineStyle: {
                    width: 1,
                    color: '#999',
                },
            },
            splitLine: {
                distance: -52,
                length: 14,
                lineStyle: {
                    width: 2,
                    color: '#999',
                },
            },
            axisLabel: {
                distance: -5,
                color: '#999',
                fontSize: 16,
            },
            anchor: {
                show: false,
            },
            title: {
                show: false,
            },
            detail: {
                valueAnimation: true,
                width: '60%',
                lineHeight: 40,
                borderRadius: 8,
                offsetCenter: [0, '-50%'],
                fontSize: 30,
                fontWeight: 'bolder',
                formatter: '{value} ',
                color: 'inherit',
            },
            data: [{ value: item.value }],
        },
    ],
});

export const updateGauges = (energyData) => {
    energyData.forEach(item => {
        const chartDom = document.getElementById(`gauge-${item.id}`);
        if (chartDom) {
            chartDom.style.border = '1px solid #ccc';
            chartDom.style.boxShadow = '0 0 3px white';
            chartDom.style.borderRadius = '10px';
            chartDom.style.display = 'flex';
            chartDom.style.alignItems = 'center';
            chartDom.style.justifyContent = 'center'; 
            chartDom.style.height = '250px'; 
            

            const myChart = echarts.getInstanceByDom(chartDom) || echarts.init(chartDom);
            myChart.setOption(getGaugeOption(item));
        }
    });
}