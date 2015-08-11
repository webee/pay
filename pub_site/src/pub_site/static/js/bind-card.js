$(document).ready(function () {

    $("#card_number").bankInput();

    var provinceToCitiesMap = {};

    function renderCitySelect(cities) {
        var citySelect = $('.city');
        citySelect.empty();
        $.each(cities, function (index, city) {
            citySelect.append($('<option></option>').attr('value', city[0]).text(city[1]));
        });
    }

    $('.province').change(function () {
        var selectedProvinceCode = $(this).children('option:selected').val();
        if(!provinceToCitiesMap[selectedProvinceCode]) {
            $.get('/data/provinces/' + selectedProvinceCode + '/cities', function (result, textStatus) {
                if (textStatus === 'success') {
                    provinceToCitiesMap[selectedProvinceCode] = result.data;
                    renderCitySelect(provinceToCitiesMap[selectedProvinceCode]);
                }
            });
        } else {
            renderCitySelect(provinceToCitiesMap[selectedProvinceCode]);
        }

    });
    $('#submit').click(function(){
        $('#main').showLoading();
    });
});