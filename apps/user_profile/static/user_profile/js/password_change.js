$("#btn-submit").prop("disabled", true);

$("input[type='password']").not("#id_old_password").each(function(idx, li) {
	$(li).attr("readonly", true);
	});


$('#password-change-form input').on('input', function(e) {
	e.preventDefault();

	password = $("#id_password").val();
	oldPassword = $("#id_old_password").val();

	$.ajax({
		type: "POST",
		url: window.location.href,
		data: {
			'password': password,
			'old_password': oldPassword,
		},

		success: function(response) {
			errorDict = response['error_list'];
			passwordErrorArray = errorDict['password'];

			inputArray = ["#id_old_password", "#id_password"];
			errorArray = [null, passwordErrorArray];

			validatePassword(
				errorIdArray, errorMsgArray,
				personalId, personalErrorArray,
				passwordErrorArray
			);
			passwordStrength("#password-border li", ".progress-bar");			
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