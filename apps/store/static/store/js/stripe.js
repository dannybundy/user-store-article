// STRIPE CODE

// Create an instance of Elements.
var elements = stripe.elements();

// Custom styling can be passed to options when creating an Element.
// (Note that this demo uses a wider set of styles than the guide below.)
var style = {
  base: {
    color: '#32325d',
    fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
    fontSmoothing: 'antialiased',
    fontSize: '16px',
    '::placeholder': {
      color: '#aab7c4'
    }
  },
  invalid: {
    color: '#fa755a',
    iconColor: '#fa755a'
  }
};

// Create an instance of the card Element.
var card = elements.create('card', {style: style});

// Add an instance of the card Element into the `card-element` <div>.
card.mount('#card-element');
// Handle real-time validation errors from the card Element.
card.on('change', function(event) {
  var displayError = document.getElementById('card-errors');
  if (event.error) {
    displayError.textContent = event.error.message;
  } else {
    displayError.textContent = '';
  }

});


card.on('focus', function(event) {
  card.clear();
});

card.on('change', function(event) {
  if (event.complete) {
    $("#stripeBtn").focus();
  }
});


$(".loader").hide();

$("#stripe-form").on("submit", function(e) {
  $("#stripeBtn").hide();
  $(".loader").show();

  if (storedCard){
    console.log("No Stripe JS");
  } else {
    console.log("Stripe JS");

    // SOURCE
    // Handle form submission.
    event.preventDefault();

    stripe.createSource(card).then(function(result) {
      if (result.error) {
        $("#stripeBtn").show();
        $(".loader").hide();
        // Inform the user if there was an error.
        var errorElement = document.getElementById('card-errors');
        errorElement.textContent = result.error.message;
      } else {
        // Send the token to your server.
        stripeSourceHandler(result.source);
      }
    });


    // Submit the form with the source ID.
    function stripeSourceHandler(source) {
      // Insert the token ID into the form so it gets submitted to the server
      var form = document.getElementById('stripe-form');
      var hiddenInput = document.createElement('input');
      hiddenInput.setAttribute('type', 'hidden');
      hiddenInput.setAttribute('name', 'stripeToken');
      hiddenInput.setAttribute('value', source.id);
      form.appendChild(hiddenInput);

      // Submit the form
      form.submit();
    }

  }

});