$(document).ready(function() {
    const convertToFloatWithDot = (value) => Number(value.replace(',', '.'));
    $('#device_search').submit(function(event) {
        event.preventDefault();
        $('#spinner-one').attr('hidden', false);
        document.getElementById('device_content').innerHTML = "";
        search_field = document.querySelector("#search_input").value;
        $.ajax({
            type: "GET",
            url: 'get-device-info/',
            data: {'search_field': search_field}
        })
        .done(function(response) {
            setTimeout(() => {
                                $('#spinner-one').attr('hidden', true);
                                $('#device_content').append(response);
                                document.getElementById("search_input").focus();
                                var date_list = [];   // Массив для дат (1-й столбец)
                                var meter_list = [];  // Массив для показаний (3-й столбец)
                                // Обрабатываем каждую строку тела таблицы
                                $('#device-info-table tbody tr').each(function(index, element){
                                    // Извлекаем первую ячейку (дата)
                                    date_list.push($(element).find('td:eq(1)').text().trim());
                                    // Извлекаем третью ячейку (показания)
                                    meter_list.push($(element).find('td:eq(2)').text().trim());
                                });
                                var convertedData = meter_list.map(convertToFloatWithDot);
                                let ser_massiv = [
                                    {
                                        name: 'Показания',
                                        data: convertedData.reverse(), // копируем и переворачиваем массив
                                    },
                                ];
                                const date_list_reverse = date_list.reverse()
                                createLineChart(ser_massiv, date_list, 'chart');
                                }, 250);
        });
    });
});
