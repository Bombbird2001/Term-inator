var hosturl = window.location.hostname;
const suffixes = [".com", ".org", ".co", ".gov"];

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
			var tc = xhttp.responseText;
			console.log("tc: " + JSON.parse(tc));
		}
	};
	var data = JSON.stringify({"html": html, "domain": domain, "url": tclink});
	//console.log(html);
	xhttp.send(data);
}

function sendLink(url, domain) {
	chrome.runtime.sendMessage({type: "getHtml", tclink: url}, function(response) {
		//Once html from web is received, send to server for processing
		var rhtml = response.html;
		//console.log("response html: " + rhtml);
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
			console.log("tclink: " + tclink);
			//Once ready, run sendLink to get link of T&C from server (background function)
			if (tclink != "Failed to retrieve link") {
				//If server finds the link successfully, send link to background
				sendLink(tclink, domain);
			}
		}
	};
	var data = JSON.stringify({"domain": domain});
	console.log(data)
	xhr.send(data);
}

//Get domain name from page url (local function)
var domain = getDomain(hosturl);
console.log(domain);
//Get terms of service link from server (local function)
getLinkFromPage(domain);