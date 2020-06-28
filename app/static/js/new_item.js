$(document).ready(function(){
$("#itemBrand").select2({
    minimumInputLength: 1,
    ajax: {
        url: "{{url_for('api.get_brands')}}",
        dataType: 'json',
        type: "GET",
        quietMillis: 50,
        data: function (params) {
          return {
            term: params.term // search term
          };
        },
        results: function (data) {
            return {
                results: data.items
            };
        }
    }
});
$("#itemStyle").select2({
    minimumInputLength: 1,
    ajax: {
        url: "{{url_for('api.get_styles')}}",
        dataType: 'json',
        type: "GET",
        quietMillis: 50,
        data: function (params) {
          return {
            term: params.term // search term
          };
        },
        results: function (data) {
            return {
                results: data.items
            };
        }
    }
});


});