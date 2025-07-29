const startPU = document.getElementById("startPU");
const startBS = document.getElementById("startBS");

startPU.addEventListener("click", function(event) {
    document.getElementById('spinner-pu').style.visibility = 'visible';
    $('#startPU').attr('disabled', true);
    var token = $('input[name="csrfmiddlewaretoken"]').attr('value');
    console.log("Кнопка нажата startPU!");
    $.ajax({
        type: 'POST',
        url: 'start/',
        data: {'request_type': 'startPU',
               'csrfmiddlewaretoken': token,
                             },
        dataType: 'json',
        success: function(response) {
            if (response.success) {
                 document.getElementById('spinner-pu').style.visibility = 'hidden';
                 $('#startPU').attr('disabled', false);
            } else {
            }
        },
        error: function(response) {
           // Do something on error
        }
    });
});

startBS.addEventListener("click", function(event) {
    document.getElementById('spinner-bs').style.visibility = 'visible';
    $('#startBS').attr('disabled', true);
    var token = $('input[name="csrfmiddlewaretoken"]').attr('value');
    console.log("Кнопка нажата startBS!");
    $.ajax({
        type: 'POST',
        url: 'start/',
        data: {'request_type': 'startBS',
               'csrfmiddlewaretoken': token,
                             },
        dataType: 'json',
        success: function(response) {
            if (response.success) {
                document.getElementById('spinner-bs').style.visibility = 'hidden';
                $('#startBS').attr('disabled', false);
            } else {
            }
        },
        error: function(response) {
           // Do something on error
        }
    });
});
