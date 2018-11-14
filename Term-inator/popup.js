chrome.runtime.onMessage.addListener(
	function(request, sender, sendResponse) {
		if (request.type == "sendUI") {
			console.log("Received!");
			var parsedTc = request.data;
			console.log("tclink: " + parsedTc);
		}
	});

$(".btn.important").click(function(){

});

$(".btn.paste").click(function(){

});

$(".btn.others").click(function(){

});
