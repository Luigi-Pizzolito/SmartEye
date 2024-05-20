jQuery( document ).ready(function() {

    $(window).scroll(function(){
    $('.topnav').toggleClass('scrollednav py-0', $(this).scrollTop() > 50);
    });
    
});

// *******************************************************************
// * Author: 2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
// *******************************************************************

// State variables

// Stream list
streamList = {
    Streams: [
        "camera0-stream",
        "camera0-gesture-stream",
        "camera0-pose-stream",
        "camera0-faces-stream"
    ],
    FPS: {
        "camera0-stream": 10,
        "camera0-gesture-stream": 15,
        "camera0-pose-stream": 20,
        "camera0-faces-stream": 8
    }
}
// AI Process Output
AIdata = {}

// Generate stream's HTML
function generateHTML(streamList) {
    const streams = streamList.Streams;
    // Sort streams by string length
    streams.sort((a, b) => a.length - b.length);
    const container = document.getElementById("stream-container");
    removeAllChildren("stream-container");

    let streamCounter = 0;

    while (streamCounter < streams.length) {
        const containerDiv = document.createElement("div");
        containerDiv.classList.add("container");

        const rowDiv = document.createElement("div");
        rowDiv.classList.add("row", "justify-content-between");

        for (let i = 0; i < 2 && streamCounter < streams.length; i++) {
            const stream = streams[streamCounter];
            const streamName = stream.replace(/-/g, " ");
            const streamTitle = streamName.charAt(0).toUpperCase() + streamName.slice(1);

            const colDiv = document.createElement("div");
            colDiv.classList.add("col-md-6", "pt-4");

            const h4 = document.createElement("h4");
            h4.classList.add("font-weight-bold", "spanborder");
            const span = document.createElement("span");
            span.textContent = streamTitle;
            h4.appendChild(span);

            const img = document.createElement("img");
            img.src = `http://localhost:8095/${stream}.mjpeg`;

            const imgDiv = document.createElement("div")
            imgDiv.classList.add("pr-3")
            imgDiv.appendChild(img)

            const fpsParagraph = document.createElement("p");
            fpsParagraph.textContent = "\u00B7 FPS : 0fps";
            fpsParagraph.id = `${stream}-fps`;

            const fpsDiv = document.createElement("div");
            fpsDiv.classList.add("pt-1", "card-text", "text-muted", "small");
            fpsDiv.appendChild(fpsParagraph);

            const innerDiv = document.createElement("div");
            innerDiv.classList.add("mb-3", "d-flex", "justify-content-between");
            imgDiv.appendChild(fpsDiv);
            innerDiv.appendChild(imgDiv);

            colDiv.appendChild(h4);
            colDiv.appendChild(innerDiv);

            rowDiv.appendChild(colDiv);

            streamCounter++;
        }

        containerDiv.appendChild(rowDiv);
        container.appendChild(containerDiv);
    }
}

function removeAllChildren(containerId) {
    const container = document.getElementById(containerId);
    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }
}

// Dynamically update streams, FPS, AI Data
updated = false
function documentLoaded() {
    updateListfromBackend()
    checkUpdated();
    window.setInterval(updateListfromBackend, 1000)
    // window.setInterval(checkUpdated, 30000)
    window.setInterval(updateAIDatafromBackend, 200)
}

function checkUpdated() {
    if (updated === false) {
        window.setTimeout(checkUpdated, 100)
    } else {
        updated = false
        generateHTML(streamList);
    }
}

function updateFPS() {
    const FPS = streamList.FPS;
    Object.keys(FPS).forEach(stream => {
        const fps = FPS[stream];
        const element = document.getElementById(stream + "-fps");
        if (element) {
            element.textContent = `· Frame rate: ${fps}fps`;
        }
    });
}

function updateListfromBackend() {
    fetch('http://localhost:8095/list')
    .then(response => response.json())
    .then(data => {
        streamList = data
        updateFPS()
        updated = true
    })
    .catch(error =>console.error('Error fetching stream list:', error))
}

function updateAIDatafromBackend(){
    fetch('http://localhost:8200/data')
    .then(response => response.json())
    .then(data => {
            try {
                changes = detectChanges(AIdata, data)
                changes = reorganizeChanges(changes)
                if (!(Object.keys(changes).length === 0)) {
                    // changes detected
                    // console.log(JSON.stringify(changes))
                    outputLogMessages(changes)
                }
                AIdata = data

            } catch (error) {
                console.error("Failed to parse AI Data changes: ", error)
            }
    })
    .catch(error =>console.error('Error fetching AI Data:', error))
}


function detectChanges(oldStruct, newStruct) {
    const changes = {};

    // Loop through each camera in the structure
    for (const cameraKey in oldStruct) {
        if (oldStruct.hasOwnProperty(cameraKey) && newStruct.hasOwnProperty(cameraKey)) {
            const oldCamera = oldStruct[cameraKey];
            const newCamera = newStruct[cameraKey];

            changes[cameraKey] = {};

            // Loop through each key in the camera object
            for (const key in oldCamera) {
                if (oldCamera.hasOwnProperty(key) && newCamera.hasOwnProperty(key)) {
                    // Compare the values of the keys
                    if (key == "faces") {

                        if (!arraysAreEqual(oldCamera["faces"], newCamera["faces"])) {
                            changes[cameraKey][key] = {
                                oldValue: oldCamera[key],
                                newValue: newCamera[key]
                            };
                        }
                    } else if (oldCamera[key] != newCamera[key]) {
                        changes[cameraKey][key] = {
                            oldValue: oldCamera[key],
                            newValue: newCamera[key]
                        };
                    }
                }
            }
        }
    }
    deleteEmptyKeys(changes)
    return changes;
}

function arraysAreEqual(arr1, arr2) {
    // Check if the arrays have the same length
    if (arr1.length !== arr2.length) {
        return false;
    }

    // Check if each element in the arrays is equal
    for (let i = 0; i < arr1.length; i++) {
        if (arr1[i] !== arr2[i]) {
            return false;
        }
    }

    // If all elements are equal, return true
    return true;
}

function deleteEmptyKeys(obj) {
    for (let key in obj) {
        if (typeof obj[key] === 'object' && Object.keys(obj[key]).length === 0) {
            delete obj[key];
        }
    }
}

function reorganizeChanges(obj) {
    // Remove all "oldValue" keys
    function removeOldValueKeys(obj) {
        for (let key in obj) {
            if (typeof obj[key] === 'object') {
                removeOldValueKeys(obj[key]); // Recursively call function for nested objects
            } else if (key === "oldValue") {
                delete obj[key]; // Delete "oldValue" key
            }
        }
    }
    
    removeOldValueKeys(obj);

    // Reorganize the object into separate objects for faces, hands, and pose changes
    let faces_change = {};
    let hands_change = {};
    let pose_change = {};

    for (let camera in obj) {
        if (obj[camera].hasOwnProperty("faces")) {
            let val = obj[camera]["faces"]["newValue"];
            if (val.length != 0 /*&& val[0] !== "Unknown"*/) {
                faces_change[camera] = val
            }
        } else if (obj[camera].hasOwnProperty("hand")) {
            let val = obj[camera]["hand"]["newValue"];
            if (val != null && val != "") {
                hands_change[camera] = val
            }
        } else if (obj[camera].hasOwnProperty("fall")) {
            let val = obj[camera]["fall"]["newValue"]
            if (val != null && val != "") {
                pose_change[camera] = val;
            }
        }
    }

    return { faces_change, hands_change, pose_change };
}

function outputLogMessages(changes) {
    const timestamp = new Date().toISOString();

    if (changes.faces_change) {
        const changesObj = changes.faces_change;
        for (const camera in changesObj) {
            const state = changesObj[camera];
            const message = `[${timestamp}] Camera ${camera}: Face detected: ${state}\n`;
            document.getElementById('detect-face').value += message;
        }
        scrollToBottom('detect-face');
    }

    if (changes.hands_change) {
        const changesObj = changes.hands_change;
        for (const camera in changesObj) {
            const state = changesObj[camera];
            const message = `[${timestamp}] Camera ${camera}: Hand detected, gesture: ${state}\n`;
            document.getElementById('detect-hand').value += message;
        }
        scrollToBottom('detect-hand');
    }

    if (changes.pose_change) {
        const changesObj = changes.pose_change;
        for (const camera in changesObj) {
            const state = changesObj[camera];
            const message = `[${timestamp}] Camera ${camera}: Pose detected, state: ${state}\n`;
            document.getElementById('detect-fall').value += message;
            if (state == "fall") {
                // alert(message)
                showNotification(message)
            }
        }
        scrollToBottom('detect-fall');
    }
}

function scrollToBottom(id) {
    const textarea = document.getElementById(id);
    textarea.scrollTop = textarea.scrollHeight;
}


function showNotification(text) {
    // Check if the browser supports notifications
    if (!("Notification" in window)) {
      console.error("This browser does not support desktop notification");
      return;
    }
  
    // Check if notification permission is granted
    if (Notification.permission === "granted") {
      // If it's okay, create a notification
      var notification = new Notification(text);
    } else if (Notification.permission !== "denied") {
      // Otherwise, ask for permission
      Notification.requestPermission().then(function (permission) {
        // If permission is granted, create a notification
        if (permission === "granted") {
          var notification = new Notification(text);
        }
      });
    }
  }