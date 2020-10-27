$(document).ready(function () {
        $('#search').autocomplete({
            source: function (request, response) {
                $.ajax({
                    url: "/api/Elasticsearch",
                    data: { term: request.term },
                    dataType: "json",
                    success: function (data) {

                        response($.map(data.items, function (item) {
                        	
                            return {
                                name: item.name,
                                avatar: item.thumbnails,
                                brand: item.brand,
                                id: item.id
                            };
                        }))
                    }
                })
            },
            select: function (event, ui) {

              window.location.replace("/item/" + ui.item.id);

                return false;
            }
        }).data("ui-autocomplete")._renderItem = function (ul, item) {
            var inner_html = '<div class="select2-result-repository clearfix"><div class="select2-result-repository__avatar"><img src="https://d2x1mfjcaooqwx.cloudfront.net/' + item.avatar[0] + '"></div><div class="select2-result-repository__title"><h3>' + item.brand + '</h3></div><div class="select2-result-repository__description">' + item.name + '</div></div>';
            return $("<li></li>")
                    .data("ui-autocomplete-item", item)
                    .append(inner_html)
                    .appendTo(ul);
        };


   });