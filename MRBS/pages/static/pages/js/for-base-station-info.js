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
    let ser_massiv = [
        {
            name: 'Кол-во ПУ',
            data: count_list.reverse(), // копируем и переворачиваем массив
        },
    ];
    const date_list_reverse = date_list.reverse()
    createLineChart(ser_massiv, date_list_reverse, 'chart');
  });