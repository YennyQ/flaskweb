/*tags*/
$('#tokenfield').tokenfield();


$('#tokenfield').on('tokenfield:createtoken', function (event) {
	var existingTokens = $(this).tokenfield('getTokens');
	$.each(existingTokens, function(index, token) {
		if (token.value === event.attrs.value)
			event.preventDefault();
	});
});

$('#my-tokenfield').on('tokenfield:createtoken', function (event) {
	var available_tokens = bloodhound_tokens.index.datums
	var exists = true;
	$.each(available_tokens, function(index, token) {
		if (token.value === event.attrs.value)
			exists = false;
	});
	if(exists === true)
		event.preventDefault();
})