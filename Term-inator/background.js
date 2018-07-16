chrome.runtime.onInstalled.addListener(function() {
	console.log("Extension initialised.");
  chrome.storage.sync.set({color: '#3aa757'}, function() {
    console.log("Colour set to green.");
  });
});

chrome.runtime.onMessage.addListener(
	function(request, sender, sendResponse) {
		if (request.type == "getHtml") {
			//Get html from webpage
			//var xhr = new XMLHttpRequest();
			var url = request.tclink;
			console.log("tclink: " + url);
			/*
			var method = "POST";
			xhr.open(method, url, true);
			xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
			xhr.onreadystatechange = function() {
				if (xhr.readyState === 4 && xhr.status === 200) {
					var data = xhr.responseText;
					sendResponse({html: data});
					console.log("data: " + data);
				}
			};
			xhr.send();
			*/
			$.get(url, function(responseText) {
				sendResponse({html: responseText});
			});
			return true;
		}
	});