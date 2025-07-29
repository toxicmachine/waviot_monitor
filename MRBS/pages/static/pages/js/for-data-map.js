const count_on_point_but = document.getElementById("count_on_point_but");
const heatmap_but = document.getElementById("heatmap_but");

function get_map(selected_type) {
    event.preventDefault();
    $('#spinner-big').attr('hidden', false);
    document.getElementById('map-block').innerHTML = "";
    $('#bs_but').attr('disabled', true);
    $('#count_on_point_but').attr('disabled', true);
    $('#heatmap_but').attr('disabled', true);
    $.ajax({
        type: 'GET',
        url: 'map-request/',
        data: {'map_type': selected_type,
              }
    })
    .done(function(response) {
         setTimeout(() => {
                $('#spinner-big').attr('hidden', true);
                $('#map-block').append(response);
                $('#bs_but').attr('disabled', false);
                $('#count_on_point_but').attr('disabled', false);
                $('#heatmap_but').attr('disabled', false);
                }, 500);
         });
}

count_on_point_but.addEventListener("click", function(event) {
    get_map('count_on_point_map');
});

heatmap_but.addEventListener("click", function(event) {
    get_map('heatmap_map');
});