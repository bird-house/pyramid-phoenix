function initRangeSlider(field_name, options) {
	var sliderName = "#slider-" + field_name;
	$(sliderName).rangeSlider(options);
	$(sliderName).on(
			"valuesChanging",
			function(e, data) {
				document.getElementById(field_name).value = Math
						.round(data.values.min)
						+ "|" + Math.round(data.values.max);
			})
}

function initDateRangeSlider(field_name, options) {
	var sliderName = "#slider-" + field_name;
	$(sliderName).dateRangeSlider(options);
	$(sliderName).on(
			"valuesChanging",
			function(e, data) {
				document.getElementById(field_name).value = Math
						.round(data.values.min)
						+ "|" + Math.round(data.values.max);
			})
}
