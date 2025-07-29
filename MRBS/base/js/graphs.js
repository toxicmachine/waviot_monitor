function createLineChart(ser_massiv, dateList, graphElemName) {
      const options = {
            series: ser_massiv,
            chart: {
              animations: {
                enabled: false,
              },
              height: 350,
              type: 'line',
              zoom: {
                enabled: false
              },
            },
            dataLabels: {
              enabled: false
            },
            stroke: {
              curve: 'straight',
              width: 8
            },
            colors: ['#A8DADC'],
            markers: {
                size: 8,
                colors: ['#1D3557'],
            },
            grid: {
              row: {
                colors: ['#f3f3f3', 'transparent'],
                opacity: 0.5
              },
            },
            xaxis: {
              categories: dateList // копируем и переворачиваем массив
            }
      };
      const chartElement = document.getElementById(graphElemName);
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
function createPieChart(depData, depLabels, graphElemName) {
    const options = {
      series: depData.map(Number),
      chart: {
      width: 470,
      type: 'pie',
    },
    labels: depLabels,
    responsive: [{
      breakpoint: 480,
      options: {
        chart: {
          width: 200
        },
        legend: {
          position: 'bottom'
        },
      }
    }]
    };
    var chart = new ApexCharts(document.querySelector(graphElemName), options);
    chart.render();
    return chart;
}
function createSimpleLineChart(depData, depLabels, countName, graphElemName) {
        var options = {
          series: [{
          data: depData.map(Number),
          name: countName,
        }],
          chart: {
          type: 'bar',
          height: 305
        },
        plotOptions: {
          bar: {
            horizontal: true,
          }
        },
        dataLabels: {
          enabled: true
        },
        xaxis: {
          categories: depLabels,
        }
        };

        var chart = new ApexCharts(document.querySelector(graphElemName), options);
        chart.render();
        return chart;
}

function createDonutChart(dataArray_dia, headers_dia, graphElemName, colorsArray) {
        var options = {
          series: dataArray_dia.map(Number),
          colors: colorsArray,
          chart: {
              height: 450, // высота в пикселях
              width: 450,  // ширина в пикселях
              type: 'donut',
          },
          plotOptions: {
                pie: {
                    donut: {
                      size: '50%',
                      labels: {
                            show: true,
                            style: {
                                colors: ['#fff',], // устанавливаем цвета подписей
                                fontSize: '10px',
                            }
                      }
                    },
                },
          },
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
          }],
          labels: headers_dia,
        };

        var chart = new ApexCharts(document.getElementById(graphElemName), options);
        chart.render();
        return chart;
}

function createPercentageStackBar(graphElemName, rowNames, seriesArray, title, bar_height, colorsArray) {
        var options = {
            series: seriesArray,
            colors: colorsArray,
              chart: {
              type: 'bar',
              height: bar_height,
              stacked: true,
              stackType: '100%',
            },
            plotOptions: {
              bar: {
                horizontal: true,
              },
            },
            stroke: {
              width: 1,
              colors: ['#fff']
            },
            title: {
              text: title,
            },
            xaxis: {
              categories: rowNames,
            },
            tooltip: {
              y: {
                formatter: function (val) {
                  return val
                }
              }
            },
            fill: {
              opacity: 1
            },
            legend: {
              position: 'top',
              horizontalAlign: 'left',
              offsetX: 40,
              onItemClick: function(chartContext, config) {
                  return false;
                }
            },
        };

        var chart = new ApexCharts(document.getElementById(graphElemName), options);
        chart.render();
        return chart;
}