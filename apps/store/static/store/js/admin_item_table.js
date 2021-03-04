// Ajax Item Table
$(document).on('click', '.orderable', function(e) {
  e.preventDefault()
  sortValue = $(this).find('a').attr('href');
  sortValue = sortValue.split('?sort=')[1];

  $.ajax({
    type: "GET",
    url: window.location.href,
    data: {
      'sort': sortValue
    },

    success: function(response) {
      table = response['table'];
      $("#ajax-table").html(table);

    },
    error: function(response) {
      $("#random-error").append(
        `<div class="alert alert-danger alert-dismissible
          fade show text-center" role="alert">
          An error has occured. The page is going to refresh.
        </div>`
        )
      setTimeout(refreshPage, 2000);
    }

  });
});