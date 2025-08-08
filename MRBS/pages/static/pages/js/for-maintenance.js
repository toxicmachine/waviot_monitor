const restart_but = document.getElementById("restart_but");
const reload_page = document.getElementById("reload_page");

restart_but.addEventListener("click", function(event) {
    $('#restart_but').attr('disabled', true);
    document.getElementById('reload_page').style.visibility = 'visible';
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

reload_page.addEventListener("click", function(event) {
    location.reload();
});