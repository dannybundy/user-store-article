$("#btn-submit").prop("disabled",true);

$("#password-reset-confirm input").on('input', function(e) {
	e.preventDefault();

	var password = $("#password-reset-confirm").find("#id_password").val()

	$.ajax({
		type: "POST",
		url: window.location.href,
		data: {
			'password':password,
		},

		success: function(response) {
			errorDict = response['error_list'];
			passwordErrorArray = errorDict['password'];
			
			inputArray = ["#id_password"];
			errorArray = [passwordErrorArray];
			

			validatePassword(
				errorIdArray, errorMsgArray,
				personalId, personalErrorArray,
				passwordErrorArray
			);
			passwordStrength("#password_border li", ".progress-bar");			
			submitBtnHandler(inputArray, errorArray);

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

