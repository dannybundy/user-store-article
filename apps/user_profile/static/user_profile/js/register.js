$("#btn-submit").prop("disabled", true);


$("input[type='text'],[type='email'],[type='password']").not("#id_first_name").each(
	function(idx, li){
		$(li).attr("readonly", true);
	});


$('#registration-form input').on('input', function(e) {
	e.preventDefault();

	jsonData = JSON.stringify($("#registration-form").serializeArray());

	$.ajax({
		type: "POST",
		url: window.location.href,
		data: {'json_data':jsonData},

		success: function(response) {
			errorDict = response['error_list'];
			firstNameErrorArray = errorDict['first_name'];
			lastNameErrorArray = errorDict['last_name'];
			emailErrorArray = errorDict['email'];
			usernameErrorArray = errorDict['username'];
			passwordErrorArray = errorDict['password'];

			inputArray = [
				"#id_first_name", "#id_last_name",
				"#id_email", "#id_username", "#id_password"
			];

			errorArray = [
				firstNameErrorArray, lastNameErrorArray,
				emailErrorArray, usernameErrorArray, passwordErrorArray
			];

			displayError(emailErrorArray, "#id_email", "#email_error");
			displayError(usernameErrorArray, "#id_username", "#username_error");

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

