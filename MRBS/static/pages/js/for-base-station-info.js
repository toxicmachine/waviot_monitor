$(document).ready(function(){
    var date_list = [];   // Массив для имен (1-й столбец)
    var count_list = [];  // Массив для городов (3-й столбец)

    // Обрабатываем каждую строку тела таблицы
    $('#bs-info-table tbody tr').each(function(index, element){
        // Извлекаем первую ячейку (дата)
        date_list.push($(element).find('td:eq(0)').text().trim());

        // Извлекаем третью ячейку (количество пу)
        count_list.push($(element).find('td:eq(2)').text().trim());
    });
    createLineChart(count_list, date_list, 'Кол-во ПУ');
  });