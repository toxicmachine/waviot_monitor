$(document).ready(function() {
    $('#file_input').submit(function(event) {
        event.preventDefault();
        $('#spinner-one').attr('hidden', false);
        $('#success-message').attr('hidden', true);
        $('#fail-message').attr('hidden', true);
        $('#current_report_link').attr('hidden', true);
        var fileInput = $('#inputFile')[0]; // Прямой доступ к DOM-объекту
        var files = fileInput.files; // Массив файлов

        if (files.length === 0) return alert('Файл не выбран!');

        var formData = new FormData();
        formData.append('uploaded_file', files[0], files[0].name); // Третий аргумент — название файла
        var token = $('input[name="csrfmiddlewaretoken"]').attr('value');
        $.ajax({
            type: 'POST',
            url: 'load/',
            headers: {'X-CSRFToken': token},
            data: formData,
            cache: false,
            contentType: false,
            processData: false,
            success: function(response)
            {
                console.log(response.status);
                if (response.status) {
                    const linkElement = document.getElementById('current_report_link');
                    linkElement.href = response.message;
                    $('#spinner-one').attr('hidden', true);
                    $('#success-message').attr('hidden', false);
                    $('#current_report_link').attr('hidden', false);
                }
                else {
                    $('#spinner-one').attr('hidden', false);
                    $('#fail-message').attr('hidden', false);
                };
            },
            error: function(error)
            {   console.error('Ошибка:', error.responseText);
            }
        });
    });
});
