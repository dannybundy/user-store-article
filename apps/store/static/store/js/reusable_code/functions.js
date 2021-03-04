$(document).on("click", "button[value='remove']", function(){
	return window.confirm("Are you sure you want to remove this item from your cart?");
});

enableForm = function(form, addressInput) {
	$(`${form} :input`).not(addressInput).each(function(idx, li) {
		$(li).attr("required", true);
		$(li).attr("disabled", false);
	});
}


disableForm = function(form, addressInput) {
	$(`${form} :input`).not(addressInput).each(function(idx, li) {
		$(li).attr("required", false);
		$(li).attr("disabled", true);
	});
}