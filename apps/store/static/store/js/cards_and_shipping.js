storedCard = false;
nonRequiredFields = "#id_line2, #id_billing_line2";

disableForm(".add-form, .update-form", nonRequiredFields);
$(".update-form, .add-form, .back-btn, #stripe-form").hide();
$(".add-btn").show();





displayUpdateForm = function(choiceId) {
	// Selection input choice
	var choice = $(choiceId).val();
	if (choice){
		// Hide all ".update-form"s and display chosen ".update-form"
		$(".update-form, .add-form, add-btn").hide();
		$(`.update-form[id=${choice}]`).show();
	}
}


// Enables or disables form inputs depending on whether the user is creating a new instance
// or updating an instance
handleFormInputs = function(form) {
	$(".back-btn").show();
	
	// Create new instance
	if (form == ".add-form"){
		enableForm(form, nonRequiredFields);
		disableForm(".update-form", nonRequiredFields);

	// Update existing instance
	} else {
		enableForm(form, nonRequiredFields);
		disableForm(".add-form", nonRequiredFields);	
	}
}


// Hides select input, displays ".update-form", and enables its inputs
$("#id_stored_card, #id_stored_address").on("change", function() {
	if ($("#id_stored_card, #id_stored_address").val()!=""){
		$("#id_stored_card, #id_stored_address").hide();
		displayUpdateForm("#id_stored_card, #id_stored_address");
		handleFormInputs(".update-form");
	}
});


$(".add-btn").on("click", function() {
	$(".update-form, .add-btn, #id_stored_card, #id_stored_address").hide();
	$(".add-form, #stripe-form").show();

	handleFormInputs(".add-form");
});


$(".back-btn").on("click", function() {
	$(".update-form, .add-form, .back-btn, .loader, #stripe-form").hide();
	$(".add-btn, #id_stored_card, #id_stored_address").show();

	$("#id_stored_card, #id_stored_address").val("");
})



$(document).on("click", "button[name='delete']", function() {
	val = window.confirm("Are you sure you want to delete this item?");
	if (val) {
		$(this).hide();
		$(".update").hide();
		$(".loader").show();		
	};
	return val
});



if ($("#verify_password_form")) {
	$("#displayUpdateForm").click();
}