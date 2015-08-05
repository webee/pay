$(document).ready(function () {
    $('.province').change(function () {
        var selectedProvinceCode = $(this).children('option:selected').val();
        $.get('/data/provinces/' + selectedProvinceCode + '/cities', function (result, textStatus) {
            if (textStatus === 'success') {
                var citySelect = $('.city');
                citySelect.empty();
                $.each(result.data, function (index, city) {
                    citySelect.append($('<option></option>').attr('value', city[0]).text(city[1]));
                });
            }
        });
    });
});