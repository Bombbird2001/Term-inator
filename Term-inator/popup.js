var parsedTcArray;
var listContainer = document.getElementById('tc');
var pasteContainer = document.getElementById('pastebox');

chrome.runtime.onMessage.addListener(
	function(request, sender, sendResponse) {
		if (request.type == "sendUI") {
			console.log("Received!");
		  var parsedTc = request.data;
      parsedTcArray = parsedTc.split("#");
      removeWeirdElements();
      importantFunction();
		}
	});

document.getElementById("important").addEventListener("click", importantFunction);

if (parsedTcArray == undefined) {
  document.getElementById("tc").innerHTML = "Loading...";
}

function removeWeirdElements() {
  let newArray = [];
  for (let i = 0; i < parsedTcArray.length; i++) {
    if (parsedTcArray[i].length >= 10) {
      newArray.push(parsedTcArray[i]);
    }
  }
  parsedTcArray = newArray;
}

function importantFunction() {
  if (listContainer.style.display == "none") {
      listContainer.style.display = "block";
  } else {
      listContainer.style.display = "none";
  }

     // Make the list
     var listElement = document.createElement('ul');

     // Add it to the page
     listContainer.appendChild(listElement);

     // Set up a loop that goes through the items in listItems one at a time
     var numberOfListItems = parsedTcArray.length;

     for (var i = 0; i < numberOfListItems; ++i) {
         // create an item for each one
         var listItem = document.createElement('li');

         // Add the item text
         listItem.innerHTML = parsedTcArray[i];

         // Add listItem to the listElement
         listElement.appendChild(listItem);
       }
}

document.getElementById("paste").addEventListener("click", pasteFunction);

function pasteFunction (){
      if (pasteContainer.style.display == "none") {
          pasteContainer.style.display = "block";
      } else {
          pasteContainer.style.display = "none";
      }
  }
