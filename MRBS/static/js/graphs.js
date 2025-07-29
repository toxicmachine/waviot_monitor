function createLineChart(valuesList, dateList, graphPointName) {
      const options = {
            series: [{
              name: graphPointName,
              data: valuesList.reverse() // копируем и переворачиваем массив
            }],
            chart: {
              animations: {
                enabled: false,
              },
              height: 350,
              type: 'line',
              zoom: {
                enabled: false
              }
            },
            dataLabels: {
              enabled: false
            },
            stroke: {
              curve: 'straight',
              width: 10
            },
            colors: ['#A8DADC'],
            markers: {
                size: 10,
                colors: ['#1D3557'],
            },
            grid: {
              row: {
                colors: ['#f3f3f3', 'transparent'],
                opacity: 0.5
              },
            },
            xaxis: {
              categories: dateList.reverse() // копируем и переворачиваем массив
            }
      };
      const chartElement = document.getElementById("chart");
      if (!chartElement) return console.error('Элемент #chart не найден');
      const chart = new ApexCharts(chartElement, options);
      chart.render();
}
function createRadialChart(containerId, options) {
    // Убедимся, что контейнер существует
    const containerElement = document.querySelector(`#${containerId}`);

    if (!containerElement) {
        console.error(`Контейнер с id="${containerId}" не найден.`);
        return null;
    }

    // Создание нового объекта ApexCharts с указанными опциями
    const chart = new ApexCharts(containerElement, options);

    // Рендеринг графика
    chart.render();

    return chart;
}
function createPieChart(dep-data, dep-labels) {
    const options = {
      series: dep-data,
      chart: {
      width: 380,
      type: 'pie',
    },
    labels: dep-labels,
    responsive: [{
      breakpoint: 480,
      options: {
        chart: {
          width: 200
        },
        legend: {
          position: 'bottom'
        }
      }
    }]
    };

    var chart = new ApexCharts(document.querySelector("#pie-chart"), options);
    chart.render();

    return chart;
}