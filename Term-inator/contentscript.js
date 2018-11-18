var hosturl = window.location.hostname;
const suffixes = [".com", ".org", ".co", ".gov"];
var content;
var pasteContent;
var domain;
var sentOnce = false;

function getDomain(hostdomain) {
	//Replace www at start if present
	var newDomain = hostdomain.replace("www.", "");
	//Search for common suffixes and split
	for (let i = 0; i < suffixes.length; i++) {
		newDomain = newDomain.split(suffixes[i])[0];
	}
	return newDomain;
}

function getTCFromServer(html, domain, tclink) {
	var xhttp = new XMLHttpRequest();
	var url = "https://bombbird2001.pythonanywhere.com/gettc";
	xhttp.open("POST", url, true);
	xhttp.setRequestHeader("Content-Type", "application/json");
	xhttp.onreadystatechange = function() {
		if (xhttp.readyState === 4 && xhttp.status === 200) {
			var tc = "{\"tc\":" + xhttp.responseText + "}";
			content = JSON.parse(tc).tc.join("#");
			sendToUI();
		}
	};
	var data = JSON.stringify({"html": html, "domain": domain, "url": tclink});
	xhttp.send(data);
}

chrome.runtime.onMessage.addListener(
	function(request, sender, sendResponse) {
		let requestType = request.type;
		if (requestType == "getPaste") {
			let requestPaste = request.paste;
			if (requestPaste.length == 0) {
				return false;
			}
			var xhttp = new XMLHttpRequest();
			var url = "https://bombbird2001.pythonanywhere.com/getpaste";
			xhttp.open("POST", url, true);
			xhttp.setRequestHeader("Content-Type", "application/json");
			xhttp.onreadystatechange = function() {
				if (xhttp.readyState === 4 && xhttp.status === 200) {
					var tc = "{\"tc\":" + xhttp.responseText + "}";
					pasteContent = JSON.parse(tc).tc.join("#");
					sendResponse({parsed: pasteContent});
				}
			}
			var data = JSON.stringify({"paste": requestPaste});
			xhttp.send(data);
			return true;
		}
		if (requestType == "getContent") {
			sendResponse({data: content, domain: domain, sent: sentOnce});
		}
		if (reqeustType == "resumePaste") {
			sendResponse({parsed: pasteContent});
		}
	});

function sendLink(url, domain) {
	chrome.runtime.sendMessage({type: "getHtml", tclink: url}, function(response) {
		//Once html from web is received, send to server for processing
		var rhtml = response.html;
		getTCFromServer(rhtml, domain, url);
	});
}

function getLinkFromPage(domain) {
	var xhr = new XMLHttpRequest();
	var url = "https://bombbird2001.pythonanywhere.com/getlink";
	xhr.open("POST", url, true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.onreadystatechange = function() {
		if (xhr.readyState === 4 && xhr.status === 200) {
			var tclink = xhr.responseText;
			//Once ready, run sendLink to get link of T&C from server (background function)
			if (tclink != "Failed to retrieve link") {
				//If server finds the link successfully, send link to background
				sendLink(tclink, domain);
			} else {
				sendToUI();
			}
		}
	};
	var data = JSON.stringify({"domain": domain});
	xhr.send(data);
}

function sendToUI() {
	chrome.runtime.sendMessage({type: "sendUI", data: content, domain: domain}, function(response) {
		sentOnce = true;
		//No response expected
	});
}

//Get domain name from page url (local function)
domain = getDomain(hosturl);
//Get terms of service link from server (local function)
getLinkFromPage(domain);