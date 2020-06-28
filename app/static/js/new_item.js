$(document).ready(function(){
$("#itemBrand").select2({
    minimumInputLength: 1,
    ajax: {
        url: 'http://127.0.0.1:5000/api/Brand',
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
        url: 'http://127.0.0.1:5000/api/Style',
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