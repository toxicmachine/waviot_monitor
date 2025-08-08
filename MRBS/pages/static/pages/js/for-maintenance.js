const restart_but = document.getElementById("restart_but");

restart_but.addEventListener("click", function(event) {
    $('#restart_but').attr('disabled', true);
    var token = $('input[name="csrfmiddlewaretoken"]').attr('value');
    $.ajax({
        type: 'POST',
        url: 'reload-wm/',
        data: {'csrfmiddlewaretoken': token,},
        dataType: 'json',
        success: function(response) {
            if (response.success) {
                 $('#restart_but').attr('disabled', false);
            } else {
            }
        },
        error: function(response) {
           // Do something on error
        }
    });
});
