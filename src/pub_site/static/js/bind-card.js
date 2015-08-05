$(document).ready(function () {
    $('.province').change(function () {
        var selectedProvince = $(this).children('option:selected').text();
        $.get('/data/provinces/' + selectedProvince + '/cities', function (result, textStatus) {
            if (textStatus === 'success') {
                var citySelect = $('.city');
                citySelect.empty();
                $.each(result.data, function (index, city) {
                    citySelect.append($('<option></option>').attr('value', city[1]).text(city[0]));
                });
            }
        });
    });
});