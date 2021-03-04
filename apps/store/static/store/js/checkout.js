var displayInputOrStored = function(form, input, id) {
  // If new shipping address or card
  if ($(`${input}:checked`).attr('id') == id) {
    
    // Display form, enable inputs and change "required" to "true"
    if (form == "#shipping-form") {
      $("#shipping-choices").hide();
      $("#shipping-form").show()
      addressInput = '#id_line2';
    } else {
        $("#card-choices").hide();
        $("#billing-form").show()
        $("#payment-form").show();
        addressInput = '#id_billing_line2';
    }
    enableForm(form, addressInput);
    
  // If selecting stored shipping address or card
  } else {

    // Hide form, enable inputs and change "required" to "False"
    if (form == "#shipping-form") {
      $("#shipping-form").hide()
      $("#shipping-choices").show();
      addressInput = '#id_line2';
    } else {
  	    $("#card-choices").show();
        $("#billing-form").hide()
  	    $("#payment-form").hide();
  	    addressInput = '#id_billing_line2';
    }
    disableForm(form, addressInput);

  }
}



var choseStoredObject = function(inputName, optionId) {
  if ($(`input[name=${inputName}]:checked`).attr('id') == optionId){
    return true;
  }
  return false;
}



storedCard = false;

userExists = $("#user-exists");
if (userExists.length) {
  storedCard = true;
	$("#shipping-form, #billing-form, #payment-form").hide();
  disableForm("#shipping-form", "#id_line2");
  disableForm("#billing-form", "#id_billing_line2");

	$("input[name='address_option'],[name='card_option']").on('click', function() {
    
		displayInputOrStored(
      "#shipping-form",
      "input[name='address_option']",
      "id_address_option_2"
    );
		displayInputOrStored(
      "#billing-form",
      "input[name='card_option']",
      "id_card_option_2"
    );
    storedCard = choseStoredObject("card_option", "id_card_option_1");

	});

}