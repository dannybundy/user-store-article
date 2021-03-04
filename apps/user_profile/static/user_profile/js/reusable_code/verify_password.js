// Prevents styling issue with modal form
$("#password-modal").on("hidden.bs.modal", function () {
	$(".modal-backdrop").hide();
});


$(".verify-password-form").on('submit', function(e){
	e.preventDefault();
	password = $("#id_password").val()

	$.ajax({
		type: "POST",
		url: verifyUrl,
		data: {
			'password': password,
		},

		success: function(response) {
			url = response['url'];
			errorList = response['error_list'];
			refresh = response['refresh'];

			if (refresh) {
				window.location.reload();
			}
			else {
				error = errorList['password'];
				$("#id_password").val('');
				$("#error").text(error);
			}
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