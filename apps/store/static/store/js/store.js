var radioCheckbox = function(checkboxClass) {
	$(document).on("click", checkboxClass, function() {

		if ($(checkboxClass).is(":checked")) {
			$(checkboxClass).prop("checked", false);
			$(this).prop("checked", true);
		}
		$("#filter-form").submit();
	});
}


var checkSubmit = function(checkboxClass) {
	$(checkboxClass).on("click", function() {
		$("#filter-form").submit();
	});
}

checkSubmit(".item-filter");


$("#clear-filter").on("click", function() {
	if ( $(".item-filter:checked").length > 0 ) {
		$(".item-filter").prop("checked", false);
		$("#filter-form").submit();
	}
});