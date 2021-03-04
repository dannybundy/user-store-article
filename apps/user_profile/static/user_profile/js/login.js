$loginForm = $("#login-form");

$loginForm.submit(function(e) {
	e.preventDefault();

	var username = $(this).find("#id_username").val();
	var password = $(this).find("#id_password").val();
	
	$.ajax({
		type: "POST",
		url: window.location.href,
		data: {
			"username": username,
			"password": password,
		},

		success: function(response) {
			// If login is successful, redirect user
			url = response["url"];
			if (url){
				window.location.replace(url);
			}
			else {
				error = response['error_list']['username'];
				$("#error-message").text(error);

				$loginForm.find("#id_password").val("");
				$loginForm.find("#id_username").focus();
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