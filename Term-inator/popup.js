//The current tab user is at; update this variable to show correct tab
var tab = "important";
var sent = false;

//Domain of current page
var domain = "";

//Displays the list for important tab
var listContainerImportant = document.getElementById('tc');

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

document.getElementById("tc").innerHTML = "Loading...";

function updateTab() {
	//Updates the visibility of different tabs to show the correct tab
	if (tab == "important") {
		//Display important tab
		listContainerImportant.style.display = "block";
		pasteContainer.style.display = "none";
	} else if (tab == "others") {
		//Display others tab
		listContainerImportant.style.display = "none";
		pasteContainer.style.display = "none";
	} else if (tab == "paste") {
		//Display paste tab
		listContainerImportant.style.display = "none";
		pasteContainer.style.display = "block";
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

	//Set loading text to nothing
	document.getElementById("tc").innerHTML = domain;

	// Make the list
	var listElement = document.createElement('ul');

	// Add it to the page
	listContainerImportant.appendChild(listElement);

	// Set up a loop that goes through the items in listItems one at a time
	var numberOfListItems = parsedTcArray.length;

	for (var i = 0; i < numberOfListItems; ++i) {
		// create an item for each one
		var listItem = document.createElement('li');
		listElement.setAttribute("class", "listContent");

		// Add the item text
		listItem.innerHTML = parsedTcArray[i];

		// Add listItem to the listElement
		listElement.appendChild(listItem);
	}
}

function pasteFunction () {
	if (pasteContainer.style.display == "none") {
		pasteContainer.style.display = "block";
	} else {
		pasteContainer.style.display = "none";
	}
}

function sendPasted() {
	let content = document.getElementById("terms").value;
	if (content == undefined || content.length < 50 || content.split(".").length < 10) {
		document.getElementById("warning").innerHTML = "Input text is too short, it must have at least 10 sentences!";
		return;
	}
	chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
		chrome.tabs.sendMessage(tabs[0].id, {type: "getPaste", paste: content}, function(response) {
			document.getElementById("pastebox").innerHTML = "Loading...";

			let responseText = response.parsed; //This is the text we want to display, each sentence separated by a #
			console.log(responseText);
			let parsedresponseText = responseText.split("#");
			parsedresponseText = removeWeirdElements(parsedresponseText);

			if (parsedresponseText == undefined) {
				//If the data has not finished loading yet
				return;
			} //Otherwise run the code below

			//Set loading text to nothing
			document.getElementById("pastebox").innerHTML = domain;

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

				// Add listItem to the listElement
				listElement.appendChild(listItem);
			}
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
	});
}
