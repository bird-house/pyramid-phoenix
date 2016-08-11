function selectSource() {
    default_location = "${request.route_path('solrsearch', _query=[('q', query), ('page', page)])}";
    var location = $('#source-select option:selected').val();
    if (location) {
        window.location = location;
    } else {
        window.location = default_location;
    }
};