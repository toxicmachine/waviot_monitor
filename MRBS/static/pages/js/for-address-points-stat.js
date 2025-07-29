$(document).ready(function() {
    $('#address_search').submit(function(event) {
        event.preventDefault();
        $('#spinner-one').attr('hidden', false);
        document.getElementById('address_content').innerHTML = "";
        search_field = document.querySelector("#search_input").value;
        $.ajax({
            type: "GET",
            url: 'get-address-list/',
            data: {'search_field': search_field}
        })
        .done(function(response) {
            setTimeout(() => {
                                $('#spinner-one').attr('hidden', true);
                                $('#address_content').append(response);
                                document.getElementById("search_input").focus();
                                }, 250);
        });
    });
});
