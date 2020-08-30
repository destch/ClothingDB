$(document).ready(function() {
    $(".js-example-data-ajax").select2({
  ajax: {
    url: "api/Elasticsearch",
    dataType: 'json',
    delay: 500,
    data: function (params) {
      return {
        term: params.term, // search term
        page: params.page
      };
    },
    processResults: function (data, params) {
      // parse the results into the format expected by Select2
      // since we are using custom formatting functions we do not need to
      // alter the remote JSON data, except to indicate that infinite
      // scrolling can be used
      params.page = params.page || 1;

      return {
        results: data.items,
        pagination: {
          more: (params.page * 10) < data.total_count
        }
      };
    },
    cache: true
  },
  placeholder: 'Explore the Database',
  minimumInputLength: 1,
  templateResult: formatRepo,
  templateSelection: formatRepoSelection
});

function formatRepo (repo) {
  if (repo.loading) {
    return repo.name;
  }

  var $container = $(
    "<div class='select2-result-repository clearfix'>" +
      "<div class='select2-result-repository__avatar'><img src='https://d2x1mfjcaooqwx.cloudfront.net/" + repo.thumbnails[0] + "' /></div>" +
      "<div class='select2-result-repository__meta'>" +
        "<div class='select2-result-repository__title'></div>" +
        "<div class='select2-result-repository__description'></div>" +
      "</div>" +
    "</div>"
  );

  $container.find(".select2-result-repository__title").text(repo.brand);
  $container.find(".select2-result-repository__description").text(repo.name);


  return $container;
}

function formatRepoSelection (repo) {
  console.log(repo.thumbnails);
  return repo.name || repo.text;
}
});