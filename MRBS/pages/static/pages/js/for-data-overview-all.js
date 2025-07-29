$(document).ready(function(){
//      для Распределение ПУ по подразделениям (круговая диаграмма)
    var dep_list = [];   // Массив для подразделений (1-й столбец)
    var count_list = [];  // Массив для кол-ва ПУ (2-й столбец)
    var count_points = []; // Массив для кол-ва адресов (4-й столбец)

    // Обрабатываем каждую строку тела таблицы
    $('#device-count-table tbody tr').each(function(index, element){
        // Извлекаем первую ячейку (подразделение)
        dep_list.push($(element).find('td:eq(0)').text().trim());
        // Извлекаем вторую ячейку (количество пу)
        count_list.push($(element).find('td:eq(1)').text().trim());
        // Извлекаем третью ячейку (количество адресов)
        count_points.push($(element).find('td:eq(3)').text().trim());
    });
//    для таблицы опроса БС
    const table = document.getElementById('bs-history-table');
    let result = [];
    for (let i = 1; i < table.rows.length; i++) {   // начинаем перебор со второй строки
        const row = table.rows[i];
        const firstCellValue = row.cells[0].textContent.trim(); // Значение первой ячейки (ключ 'name')

        // Остальные ячейки превращаются в массив ('data')
        let otherCellsValues = Array.from(row.cells).slice(1).map(cell => cell.textContent.trim());

        // Объект с именем и остальными значениями
        result.push({
            name: firstCellValue,
            data: otherCellsValues
        });
    }
    const headerRow = table.tHead ? table.tHead.rows[0] : table.rows[0];
    const headers = Array.from(headerRow.cells).slice(1).map(cell => cell.textContent.trim());
//    для таблицы опроса ПУ
    const table2 = document.getElementById('pu-parse-count-table');
    let result2 = [];
    for (let i = 1; i < table2.rows.length; i++) {   // начинаем перебор со второй строки
        const row = table2.rows[i];
        const firstCellValue = row.cells[0].textContent.trim(); // Значение первой ячейки (ключ 'name')

        // Остальные ячейки превращаются в массив ('data')
        let otherCellsValues = Array.from(row.cells).map(cell => cell.textContent.trim());

        // Объект с именем и остальными значениями
        result2.push({
            name: firstCellValue,
            data: otherCellsValues
        });
    }
    const headerRow2 = table2.tHead ? table2.tHead.rows[0] : table2.rows[0];
    const headers2 = Array.from(headerRow2.cells).map(cell => cell.textContent.trim());
//      для круговых диаграмм опроса адресов

    const table_dia = document.getElementById('address-parse-count-table');
    // 1. Получаем строку заголовка (excluding first column)
    const headerRow_dia = table_dia.querySelector('thead tr');
    const headers_dia = Array.from(headerRow_dia.querySelectorAll('th')).slice(1).map(th => th.textContent.trim());
    // Извлекаем все строки таблицы
    const rows_dia = table_dia.querySelectorAll('tbody tr'); // учитываем tbody, если оно используется
    // Массив данных для каждой строки (без первой колонки)
    let dataArray_dia = [];
    rows_dia.forEach(row => {
        const cells_dia = row.querySelectorAll('td'); // получаем все ячейки td строки

        // Создаем новый массив, содержащий значения начиная со второй ячейки
        let rowData_dia = Array.from(cells_dia).slice(1).map(cell => cell.textContent.trim());

        dataArray_dia.push(rowData_dia); // добавляем обработанные данные строки в общий массив
    });

    const pu_total_count = Number(document.getElementById('pu_total_count').textContent);

// построение графиков
    createPieChart(count_list, dep_list, "#pie-chart");
    createSimpleLineChart(count_points, dep_list, 'Кол-во адресов', '#simple-line-chart');
//    console.log(result, headers.reverse());
//    createLineChart(result, headers.reverse(), 'chart');
    for (let i = 0; i < result.length; i++) {
        createLineChart([result[i]], headers, 'chart-' + i);
    }
    createLineChart(result2, headers2, 'pu-parse-chart');
    for (let i = 0; i < 3; i++) {
         var order_dia = i + 8
         var parse_pu_count = Number(document.getElementById('parse-order-' + order_dia).textContent);
         createDonutChart([pu_total_count-parse_pu_count, parse_pu_count], ['ПУ, НЕ обновившие данные', 'ПУ, обновившие данные'], 'pie-chart-pu-stat-' + i, ['#FF0000', '#008000']);
     }
    for (let i = 0; i < dataArray_dia.length; i++) {
        createDonutChart(dataArray_dia[i], headers_dia, 'pie-chart-points-stat-' + i, ['#FF0000', '#FFA500', '#FFFF00', '#ADFF2F', '#008000']);
    }
  });