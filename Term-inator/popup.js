const keywords = ["third party", "third parties", "opt-out", "opt out",
"arbitration", "waive", "waiver", "account", "content", "copyright", "privacy",
"stop", "terminate"];

//The current tab user is at; update this variable to show correct tab
var tab = "important";
var sent = false;

//Domain of current page
var domain = "";

//Displays the list for important tab
var listContainerImportant = document.getElementById('tc');

//Displays the list for others tab
var listContainerOthers = document.getElementById('othersList');

//Displays the pastebox
var pasteContainer = document.getElementById('pastebox');

chrome.runtime.onMessage.addListener(
	function(request, sender, sendResponse) {
		if (request.type == "sendUI") {
			console.log("Received content! (Received after window load)");
			let parsedTc = request.data;
			domain = request.domain.toUpperCase();
			if (parsedTc == undefined) {
				document.getElementById("tc").innerHTML = "Could not retrieve terms and conditions for " + domain;
				return;
			}
			let parsedTcArray = parsedTc.split("#");
			parsedTcArray = removeWeirdElements(parsedTcArray);
			importantFunction(parsedTcArray);
		}
	});

document.getElementById("important").addEventListener("click", setImportant);
document.getElementById("others").addEventListener("click", setOthers);
document.getElementById("paste").addEventListener("click", setPaste);
document.getElementById("pastebutton").addEventListener("click", sendPasted);

listContainerImportant.innerHTML = "Loading...";
listContainerOthers.innerHTML = "Loading...";

warningMsg = document.getElementById("warning");

function updateTab() {
	//Updates the visibility of different tabs to show the correct tab
	if (tab == "important") {
		//Display important tab
		listContainerImportant.style.display = "block";
		listContainerOthers.style.display = "none";
		pasteContainer.style.display = "none";
		warningMsg.style.display = "none";
	} else if (tab == "others") {
		//Display others tab
		listContainerImportant.style.display = "none";
		listContainerOthers.style.display = "block";
		pasteContainer.style.display = "none";
		warningMsg.style.display = "none";
	} else if (tab == "paste") {
		//Display paste tab
		listContainerImportant.style.display = "none";
		listContainerOthers.style.display = "none";
		pasteContainer.style.display = "block";
		warningMsg.style.display = "block";
	}
}

function setImportant() {
	tab = "important";
	updateTab();
}

function setOthers() {
	tab = "others";
	updateTab();
}

function setPaste() {
	tab = "paste";
	updateTab();
}

function removeWeirdElements(parsedTcArray) {
  let newArray = [];
  for (let i = 0; i < parsedTcArray.length; i++) {
    if (parsedTcArray[i].length >= 10) {
      newArray.push(parsedTcArray[i]);
    }
  }
  return newArray;
}

function importantFunction(parsedTcArray) {
	if (parsedTcArray == undefined) {
		//If the data has not finished loading yet
		return;
	} //Otherwise run the code below

	//Set loading text to domain
	listContainerImportant.innerHTML = domain;
	listContainerOthers.innerHTML = domain;

	// Make the list
	var listElement = document.createElement('ul');
	var listElementOthers = document.createElement('ul');

	// Add it to the page
	listContainerImportant.appendChild(listElement);
	listContainerOthers.appendChild(listElementOthers);

	// Set up a loop that goes through the items in listItems one at a time
	var numberOfListItems = parsedTcArray.length;

	for (var i = 0; i < numberOfListItems; ++i) {
		// create an item for each one
		var listItem = document.createElement('li');

		// Add the item text
		listItem.innerHTML = parsedTcArray[i];
		
		let hasKeyword = false;
		for (let j = 0; j < keywords.length; j++) {
			if (parsedTcArray[i].toLowerCase().includes(keywords[j])) {
				hasKeyword = true;
				break;
			}
		}
		
		if (hasKeyword) {
			for (let j = 0; j < keywords.length; j++) {
				let regExp = new RegExp(keywords[j], "gi");
				listItem.innerHTML = listItem.innerHTML.replace(regExp, "<span class='highlight'>" + keywords[j] + "</span>");
			}
			// Add listItem to the listElement
			listElement.appendChild(listItem);
		} else {
			//Add to listElementOthers
			listElementOthers.appendChild(listItem);
		}
	}
}

function pasteFunction () {
	if (pasteContainer.style.display == "none") {
		pasteContainer.style.display = "block";
	} else {
		pasteContainer.style.display = "none";
	}
}

function loadPaste(response) {
	let responseText = response.parsed; //This is the text we want to display, each sentence separated by a #
	let parsedresponseText = responseText.split("#");
	parsedresponseText = removeWeirdElements(parsedresponseText);

	if (parsedresponseText == undefined) {
		//If the data has not finished loading yet
		return;
	} //Otherwise run the code below

	//Set loading text to nothing
	document.getElementById("pastebox").innerHTML = "";

	// Make the list
	var listElement = document.createElement('ul');

	// Add it to the page
	pasteContainer.appendChild(listElement);

	// Set up a loop that goes through the items in listItems one at a time
	var numberOfListItems = parsedresponseText.length;

	for (var i = 0; i < numberOfListItems; ++i) {
		// create an item for each one
		var listItem = document.createElement('li');
		listElement.setAttribute("class", "listContent");

		// Add the item text
		listItem.innerHTML = parsedresponseText[i];
		
		//Highlight keywords if any
		for (let j = 0; j < keywords.length; j++) {
			let regExp = new RegExp(keywords[j], "gi");
			listItem.innerHTML = listItem.innerHTML.replace(regExp, "<span class='highlight'>" + keywords[j] + "</span>");
		}

		// Add listItem to the listElement
		listElement.appendChild(listItem);
	}
}

function sendPasted() {
	let content = document.getElementById("terms").value;
	if (content == undefined || content.length < 50 || content.split(".").length < 10) {
		warningMsg.innerHTML = "Input text is too short, it must have at least 10 sentences!";
		return;
	} else {
		warningMsg.innerHTML = "";
	}
	chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
		chrome.tabs.sendMessage(tabs[0].id, {type: "getPaste", paste: content}, function(response) {
			loadPaste(response);
		});
	});
}

window.onload = function() {
	updateTab();
	chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
		chrome.tabs.sendMessage(tabs[0].id, {type: "getContent"}, function(response) {
			console.log("Received response content! (Received on window load)");
			if (response == undefined) {
				return;
			}
			let parsedTc = response.data;
			let sent = response.sentOnce;
			domain = response.domain.toUpperCase();
			if (parsedTc == undefined) {
				console.log("Undefined response received");
				if (sent) {
					//Set loading text to could not retrieve
					document.getElementById("tc").innerHTML = "Could not retrieve terms and conditions for " + domain;
				}
				return;
			}
			let parsedTcArray = parsedTc.split("#");
			parsedTcArray = removeWeirdElements(parsedTcArray);
			importantFunction(parsedTcArray);
		});
		chrome.tabs.sendMessage(tabs[0].id, {type: "resumePaste"}, function(response) {
			console.log("Received paste content! (Received on window load)");
			if (response == undefined) {
				console.log("Paste content response undefined!");
				return;
			}
			loadPaste(response);
		});
	});
}