$('document').ready(function(){

	var $loading = $('#loadingDiv').hide();
	$(document).ajaxStart(function () {
    	$loading.show();
  	}).ajaxStop(function () {
    	$loading.hide();
  	});

	var grid = document.querySelector("#productGrid")
	var template = document.querySelector("#product")
	var page = 2
	$(window).scroll(function() {
   		if($(window).scrollTop() + $(window).height() == $(document).height()) {
       		$.ajax({
		        url: "/api/LoadItems",
		        type: 'GET',
		        dataType: 'json',
		        data: {"page": page}, // added data type
		        success: function(res) {
		        	var items = ''
		        	var results = res.results
		        	var items = []
		        	for (index = 0; index < results.length; index++){
						var clone = template.content.cloneNode(true);
						var brand = clone.querySelector(".card-title");
						var itemName = clone.querySelector(".card-text")
						var thumbnail = clone.querySelector('.card-img-top')

						thumbnail.src = 'https://d2x1mfjcaooqwx.cloudfront.net/'+results[index].thumbnails[0]
						itemName.textContent = results[index].name
						brand.textContent = results[index].brand;
						items.push(clone)
		        	}
	        		for (index = 0; index < items.length; index ++){
		        		grid.append(items[index])
		        	}
		        	page++
		        }
		    });
   		}
	});

    



});
