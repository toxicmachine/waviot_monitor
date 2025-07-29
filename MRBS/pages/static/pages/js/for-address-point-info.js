$(document).ready(function(){

function get_procent(column_number) { // Все ячейки второго столбца (столбцы нумеруются с 0)
	table = document.getElementById('pu-info-table');
    cells = [...table.querySelectorAll(`td:nth-child(${column_number})`)];
    count = cells.filter(cell => cell.textContent.includes('Нет изменений')).length;
    countRows = table.rows.length - 3;
    count = countRows - count;
    console.log(table.rows.length, countRows, count);
    percentage = ((count / countRows) * 100).toFixed(2);
    return percentage;
}
if (document.getElementById('time-1').textContent !== null) {
    var chartOptions1 = {
        series: [get_procent(4)], // Серия данных (процент заполнения круга)
        chart: {
            height: 250, // Высота диаграммы
            type: 'radialBar', // Тип диаграммы (радиальная столбчатая)
        },
        plotOptions: {
            radialBar: {
                hollow: {
                    size: '70%', // Размер отверстия внутри кругового индикатора
                },
                dataLabels: {
                    showOn: "always",
                    name: {
                      offsetY: -10,
                      show: true,
                      color: "#888",
                      fontSize: "12px"
                    },
                    value: {
                      color: "#111",
                      fontSize: "20px",
                      show: true
                    }
                }
            },
        },
        fill: {
            colors: ['#1D3557']
        },
        labels: [document.getElementById('time-1').textContent],
    };
    createRadialChart('circle-chart1', chartOptions1);
}
else {
    console.error('Элемент с id="time-1" не найден.');
}
if (document.getElementById('time-2').textContent !== null) {
    var chartOptions1 = {
        series: [get_procent(5)], // Серия данных (процент заполнения круга)
        chart: {
            height: 250, // Высота диаграммы
            type: 'radialBar', // Тип диаграммы (радиальная столбчатая)
        },
        plotOptions: {
            radialBar: {
                hollow: {
                    size: '70%', // Размер отверстия внутри кругового индикатора
                },
                dataLabels: {
                    showOn: "always",
                    name: {
                      offsetY: -10,
                      show: true,
                      color: "#888",
                      fontSize: "12px"
                    },
                    value: {
                      color: "#111",
                      fontSize: "20px",
                      show: true
                    }
                }
            },
        },
        fill: {
            colors: ['#1D3557']
        },
        labels: [document.getElementById('time-2').textContent],
    };
    createRadialChart('circle-chart2', chartOptions1);
}
else {
    console.error('Элемент с id="time-2" не найден.');
}
if (document.getElementById('time-3').textContent !== null) {
    var chartOptions1 = {
        series: [get_procent(6)], // Серия данных (процент заполнения круга)
        chart: {
            height: 250, // Высота диаграммы
            type: 'radialBar', // Тип диаграммы (радиальная столбчатая)
        },
        plotOptions: {
            radialBar: {
                hollow: {
                    size: '70%', // Размер отверстия внутри кругового индикатора
                },
                dataLabels: {
                    showOn: "always",
                    name: {
                      offsetY: -10,
                      show: true,
                      color: "#888",
                      fontSize: "12px"
                    },
                    value: {
                      color: "#111",
                      fontSize: "20px",
                      show: true
                    }
                }
            },
        },
        fill: {
            colors: ['#1D3557']
        },
        labels: [document.getElementById('time-3').textContent],
    };
    createRadialChart('circle-chart3', chartOptions1);
}
else {
    console.error('Элемент с id="time-3" не найден.');
}
});
