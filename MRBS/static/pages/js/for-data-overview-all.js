$(document).ready(function(){
    var dep_list = [];   // Массив для имен (1-й столбец)
    var count_list = [];  // Массив для городов (3-й столбец)

    // Обрабатываем каждую строку тела таблицы
    $('#device-count-table tbody tr').each(function(index, element){
        // Извлекаем первую ячейку (подразделение)
        dep_list.push($(element).find('td:eq(0)').text().trim());

        // Извлекаем третью ячейку (количество пу)
        count_list.push($(element).find('td:eq(1)').text().trim());
    });
    createPieChart(count_list, dep_list);
  });