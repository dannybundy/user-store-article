// Prevents multiple submit
$("form").on("submit", function(e) {
	if ( $(this).hasClass("form-submitted") ) {
		e.preventDefault();
	} else {
		$(this).addClass("form-submitted");
	}
});


refreshPage = function() {
	window.location.reload()
}


// Displays search parameter in html | example: "Search results for "searchParameter"
searchParameter = $("#search-parameter").text();
$('#search-label').text(` for "${searchParameter}"`);


// Displays password hidden characters after checkbox is clicked
$("#show-password").on('click', function() {	
	if ($(this).prop("checked")){
		$("#id_password").attr('type', 'text');
	} else {
		$("#id_password").attr('type', 'password');
	}
});


// Displays form errors. In this application, used for username and email
var displayError = function(errorArray, inputTag, errorTag) {
	// Error exists
	if (errorArray
		&& (jQuery.inArray("This field is required.", errorArray)) == -1
		&& (jQuery.inArray("This field cannot be null.", errorArray)) == -1
	) {
		$(inputTag).addClass("is-invalid");
		$(errorTag).text(errorArray);
	} else {
		$(inputTag).removeClass("is-invalid");
		$(errorTag).text('');
	}
}


// Functions used for "submitBtnHandler" function
/////////////////////////////////////////////////////////////

var arrayToStr = function(inputArray) {
	var str = "";

	for (var i=0; i<inputArray.length; i++){
		
		// If "i" has reached "inputArray"'s final value,
		// add final value and break loop
		if (i == inputArray.length-1){
			str += inputArray[i];
			break;
		}

		// Otherwise, add value with ", "
		str += inputArray[i]+', ';
	}
	return str;
}

var disableInput = function(inputIdListStr) {
	$(inputIdListStr).each(function(idx, li) {
		$(li).attr("readonly", true);
	});
}

var enableInput=function(inputIdListStr) {
	$(inputIdListStr).each(function(idx, li) {
		$(li).attr("readonly", false);
	});
}


// Ensures all fields are "UserProfile" form fields are filled out
// ex: "Registration", "Password change/reset"
var isEmpty = function(inputArray) {
	arrayEmpty = [];

	$(inputArray).each(function(idx, li) {
		textLength = $(li).val().length;
		arrayEmpty.push(textLength);

		// If the length value is 0, disable submit button
		if ((jQuery.inArray(0, arrayEmpty))!=-1) {
			$("#btn-submit").prop("disabled", true);
		}
	});
}

/////////////////////////////////////////////////////////////


// If there are no errors, re-enable submit button
var submitBtnHandler = function(inputArray, errorArray) {
	for (var i=0; i<=inputArray.length; i+0) {
		inputLength = $(inputArray[i]).val().length;
		
		// If an error exists at current position or if input is empty,
		// disable future inputs/submit button and break loop
		if ( (errorArray[i]
				&& jQuery.inArray("Cannot set new password as old password. Please try again.",
				errorArray[i]) == -1
			)
			|| !inputLength) {

			// "splice" gets remaining inputs from "inputArray"
			array = inputArray.splice(i+1, inputArray.length);
			inputIdListStr = arrayToStr(array);
			disableInput(inputIdListStr);
			
			$("#btn-submit").prop("disabled", true);
			break;

		// Enable next input
		} else {
			inputId = inputArray[i+1];
			enableInput(inputId);
			i++;
		}

		// If at the end of the array without any errors, enable submit button
		if (i == inputArray.length) {

			// This ensures that the show password checkbox is not checked.
			// Password can only be saved if the password characters are hidden
			if ($("#id_password").attr('type') == 'password'){
				$("#btn-submit").prop("disabled", false);
			
			} else {
				$("#btn-submit").prop("disabled", true);
			}
			break;
		}
	}
	isEmpty(inputArray);
}



// For password strength meter
////////////////////////////////////////////////////////////


// Validates password and changes requirement list text color to green(valid) or red(error)
var validatePassword = function(
	errorIdArray, errorMsgArray, // empty password element to and possible backend error messages
	personalId, personalErrorArray,

	passwordErrorArray // actual password errors
) {
	// Checking if a value from "errorMsgArray" (error message from backend) exists
	for (var i=0; i < errorMsgArray.length; i++) {
		if ($("#id_password").val()){
			if ((jQuery.inArray(errorMsgArray[i], passwordErrorArray)) != -1){
				$(errorIdArray[i]).css('color','red')
			} else {
				$(errorIdArray[i]).css('color','green')			
			}
		} else {
			$(errorIdArray[i]).css('color','black')
		}
	}

	// Checks if password is too similar to personal info
	for (var i=0; i < personalErrorArray.length; i++) {	
		if ($("#id_password").val()){	
			if ((jQuery.inArray(personalErrorArray[i], passwordErrorArray)) != -1){
				$(personalId).css('color', 'red')
				break;
			} else {
				$(personalId).css('color', 'green')			
			}
		}
		else {
			$(personalId).css('color', 'black')
		}
	}

}

// Changes length and color of meter according to how many password requirements have been met
var passwordStrength = function(passwordListId, progressbarId) {
	// If there's an error, adds 'true' to array, else adds 'false' to array
	errorBooleanArray = [];

	$(passwordListId).each(function(idx, li) {
		if ($(li).css('color') == 'rgb(0, 128, 0)') {
			errorBooleanArray.push(true);
		} else {
			errorBooleanArray.push(false);
		}
	});

	// Checks to see how many requirements are met
    var count = 0;
    $.each(errorBooleanArray, function(i,v) {
    	if (v == true) count++; });
    if (count < 1) {
      	$(progressbarId).css('width', 0+"%");
    } else if (count == 1) {
    	$(progressbarId).css('width', 10+"%");
    } else if (count == 2) {
    	$(progressbarId).css('width', 20+"%");
    } else if (count == 3) {
    	$(progressbarId).css('width', 30+"%");
    }

    // Red - invalid password (submit button is disabled)
    if (count < 5){
    	$(progressbarId).addClass('bg-danger').removeClass('bg-warning bg-success');
    }

    // Yellow - valid but could be stronger (submit button is enabled)
    if (count == 5){
    	$(progressbarId).addClass('bg-warning').removeClass('bg-danger bg-success');
		$(progressbarId).css('width', 50+"%")

    	passwordLength = $("#id_password").val().length

    	// Green - strong
    	if (passwordLength >= 13){
	    	$(progressbarId).addClass('bg-success').removeClass('bg-danger bg-warning');
	    	$(progressbarId).css('width', 60+"%")
	    }
    	if (passwordLength >= 18){
	    	$(progressbarId).css('width', 80+"%")
	    }
    	if (passwordLength >= 22){
	    	$(progressbarId).css('width', 100+"%")
	    }
	}
}