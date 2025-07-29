$(document).ready(function(){
    const table_all = document.getElementById('address-parse-count-table-all');
    const headers_all = Array.from(table_all.querySelectorAll('th')).slice(1, -1); // берём все кроме первого и последнего
    let result_all = [];

    headers_all.forEach((header, index) => {
      const columnName = header.textContent.trim(); // Название столбца
      let dataValues = []; // Массив значений

      // Перебор строк таблицы
      table_all.querySelectorAll('tbody tr').forEach(row => {
          if (row.cells.length > index + 1 && row.cells[index + 1].textContent !== '') {
              // Преобразование содержимого ячейки в число
              dataValues.push(Number(row.cells[index + 1].textContent));
          }
      });

      // Добавляем объект в результирующий массив
      result_all.push({ name: columnName, data: dataValues });
    });


    const table_deps= document.getElementById('address-parse-count-table-deps');
    let result_deps = [];
    headers_all.forEach((header, index) => {
      const columnName = header.textContent.trim(); // Название столбца
      let dataValues = []; // Массив значений

      // Перебор строк таблицы
      table_deps.querySelectorAll('tbody tr').forEach(row => {
          if (row.cells.length > index + 1 && row.cells[index + 1].textContent !== '') {
              // Преобразование содержимого ячейки в число
              dataValues.push(Number(row.cells[index + 1].textContent));
          }
      });

      // Добавляем объект в результирующий массив
      result_deps.push({ name: columnName, data: dataValues });
    });

    const rows = table_deps.querySelectorAll('tbody tr'); // Получаем все строки
    // Формируем массив из элементов первого столбца
    const firstColumnDeps = Array.from(rows).map(row => row.cells[0].textContent.trim());

    const pu_parsed_count = Number(document.getElementById('pu_parsed_count').textContent);
    const pu_total_count = Number(document.getElementById('pu_total_count').textContent);
    let result_pu_all = [];
    result_pu_all.push({name: 'Приборы учета, НЕ обновившие данные', data: [pu_total_count-pu_parsed_count]});
    result_pu_all.push({name: 'Приборы учета, обновившие данных', data: [pu_parsed_count]});

    const table_pu_deps= document.getElementById('parse-pu-count-table-for-dep');
    const rows_pu = table_pu_deps.querySelectorAll('tbody tr'); // Получаем все строки
    const firstColumnDepsPU = Array.from(rows_pu).map(row => row.cells[0].textContent.trim());
    const headers_pu_all = Array.from(table_pu_deps.querySelectorAll('th')).slice(1, -1);
    let result_pu_deps = [];
    headers_pu_all.forEach((header, index) => {
      let dataValues = []; // Массив значений
      var columnName = '';
      // Перебор строк таблицы
      table_pu_deps.querySelectorAll('tbody tr').forEach(row => {
          if (row.cells.length > index + 1 && row.cells[index + 1].textContent !== '') {
              if (index == 0) {
              columnName = 'Приборы учета, обновившие данных'; // Название столбца
              dataValues.push(Number(row.cells[index + 1].textContent));
              }
              else if (index == 1) {
              columnName = 'Приборы учета, НЕ обновившие данные'; // Название столбца
              dataValues.push(Number(row.cells[index + 1].textContent) - Number(row.cells[index].textContent));
              };
          }
      });

      // Добавляем объект в результирующий массив
      result_pu_deps.push({ name: columnName, data: dataValues });
    });


    createPercentageStackBar('stack-bar-chart-pu-stat-all',
                             ['ТОСК'],
                             result_pu_all,
                             'Процентное соотношение ПУ, обновивших данных, и количества ПУ',
                             176,
                             ['#FF0000', '#008000'],
    );
    createPercentageStackBar('stack-bar-chart-pu-stat-for-dep',
                             firstColumnDepsPU,
                             result_pu_deps.reverse(),
                             'Процентное соотношение ПУ, обновивших данных, и количества ПУ по подразделениям',
                             540,
                             ['#FF0000', '#008000'],
                             );
    createPercentageStackBar('stack-bar-chart-points-stat-all',
                             ['ТОСК'],
                             result_all,
                             'Процентное соотношение опроса по адресам по организации',
                             217,
                             ['#FF0000', '#FFA500', '#FFFF00', '#ADFF2F', '#008000'],
    );
    createPercentageStackBar('stack-bar-chart-points-stat',
                             firstColumnDeps,
                             result_deps,
                             'Процентное соотношение опроса по адресам по подразделениям',
                             540,
                             ['#FF0000', '#FFA500', '#FFFF00', '#ADFF2F', '#008000'],
                             );
  });