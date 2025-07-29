$(document).ready(function(){
//    для таблицы опроса БС
    const table_bs = document.getElementById('bs-history-table');
    // Массив для хранения объектов каждой строки
    let result_bs = [];
    // Пропускаем первую строку там заголовок (header)
    for (let i = 1; i < table_bs.rows.length; i++) {   // начинаем перебор со второй строки
        const row = table_bs.rows[i];
        // Остальные ячейки превращаются в массив ('data')
        let otherCellsValues = Array.from(row.cells).map(cell => cell.textContent.trim());
        // Объект с именем и остальными значениями
        result_bs.push({
            name: 'Кол-во ПУ',
            data: otherCellsValues
        });
    }
    const headerRow_bs = table_bs.tHead ? table_bs.tHead.rows[0] : table_bs.rows[0];
    const headers_bs = Array.from(headerRow_bs.cells).map(cell => cell.textContent.trim());
//    для таблицы опроса ПУ
    const table_pu = document.getElementById('pu-parse-count-table');
    // Массив для хранения объектов каждой строки
    let result_pu = [];
    // Пропускаем первую строку там заголовок (header)
    for (let i = 1; i < table_pu.rows.length; i++) {   // начинаем перебор со второй строки
        const row = table_pu.rows[i];
        // Остальные ячейки превращаются в массив ('data')
        let otherCellsValues = Array.from(row.cells).map(cell => cell.textContent.trim());
        // Объект с именем и остальными значениями
        result_pu.push({
            name: 'Кол-во ПУ',
            data: otherCellsValues
        });
    }
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

    const headerRow_pu = table_pu.tHead ? table_pu.tHead.rows[0] : table_pu.rows[0];
    const headers_pu = Array.from(headerRow_pu.cells).map(cell => cell.textContent.trim());
    createLineChart(result_pu, headers_pu, 'pu-parse-chart');
    createLineChart(result_bs, headers_bs, 'bs-parse-chart');
    for (let i = 0; i < 3; i++) {
         var order_dia = i + 8
         var parse_pu_count = Number(document.getElementById('parse-order-' + order_dia).textContent);
         createDonutChart([pu_total_count-parse_pu_count, parse_pu_count], ['ПУ, НЕ обновившие данные', 'ПУ, обновившие данные'], 'pie-chart-pu-stat-' + i, ['#FF0000', '#008000']);
    }
    for (let i = 0; i < dataArray_dia.length; i++) {
        createDonutChart(dataArray_dia[i], headers_dia, 'pie-chart-points-stat-' + i, ['#FF0000', '#FFA500', '#FFFF00', '#ADFF2F', '#008000']);
    }
  });