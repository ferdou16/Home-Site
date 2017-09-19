$("#mailing-check").change(function () {
	if(this.checked)
		$("#mailing-volunteerdiv").css("display", "inline");
	else
		$("#mailing-volunteerdiv").css("display", "none");
});
