// ********************************************************************
//    * Author: 2024 Jingdi Lei (@https://github.com/kyrieLei)
//    *         2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
// ********************************************************************
var sockaddr = "ws://localhost:8100"
var socket=new WebSocket(sockaddr)
//* Send function which automatically reconnects if socket is closed, added by Luigi Pizzolito
async function WSsend(message) {
    if (socket.readyState === WebSocket.CLOSED) {
        socket.close();
        socket = new WebSocket(sockaddr)
        while (socket.readyState !== WebSocket.OPEN) {
            await new Promise(r => setTimeout(r, 250))
        }
    }
    socket.send(message)
}

const faceReg=document.getElementById('faceReg')
const faceSave=document.getElementById('faceSaved')
const faceLoad=document.getElementById('faceLoad')

faceReg.addEventListener('click',()=>{
    WSsend(JSON.stringify({action:'r'}));
});

faceSave.addEventListener('click',()=>{
    WSsend(JSON.stringify({action:'s'}));
});

faceLoad.addEventListener('click',()=>{
    WSsend(JSON.stringify({action:'q'}));
});

navigator.mediaDevices.getUserMedia({video:true})
// .then((stream)=>{
//    const videoElement=document.getElementById('videoElement');
//    videoElement.srcObject=stream
// })
.then(function(stream) {
    // -- transmit images to server via websocket
    const videoElement=document.getElementById('videoElement');
    videoElement.srcObject=stream;
    const video = document.createElement('video');
    video.srcObject = stream;
    video.play();

    setInterval(function() {

        //* call new function
        sendScreenshot(videoElement)

        // const canvas = document.createElement('canvas');
        // const ctx = canvas.getContext('2d');
        // canvas.width = video.videoWidth;
        // canvas.height = video.videoHeight;
        // ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        // canvas.toBlob(function(blob) {
        //     if (socket.readyState === WebSocket.OPEN) {
        //         WSsend(blob);
        //     }
        // }, 'image/jpeg', 0.9); // JPEG格式，质量为0.9
    }, 1000 / 1); // 假设1fps //* frame rate reduced to 1fps
})
.catch((error)=>{
    WSsend(JSON.stringify({action:"ERROR"}))
})

//* Functions added by Luigi Pizzolito to take a frame from the video element and send
//* as JPEG encoded binary buffer over websocket
async function captureScreenshot(videoElement) {
    return new Promise((resolve, reject) => {
        // Create a canvas element
        const canvas = document.createElement('canvas');
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;

        // Draw the current frame of the video onto the canvas
        const context = canvas.getContext('2d');
        context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

        // Convert the canvas content to a blob with JPEG encoding and 0.9 quality
        canvas.toBlob((blob) => {
            if (blob) {
                resolve(blob);
            } else {
                reject(new Error('Failed to create blob'));
            }
        }, 'image/jpeg', 0.9);
    });
}

function blobToArrayBuffer(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsArrayBuffer(blob);
    });
}

async function sendScreenshot(videoElement) {
    try {
        const blob = await captureScreenshot(videoElement);
        const arrayBuffer = await blobToArrayBuffer(blob);

        // Send the ArrayBuffer through the WebSocket
        WSsend(arrayBuffer);
        console.log('Screenshot sent via WebSocket.');
    } catch (error) {
        console.error('Error capturing or sending screenshot:', error);
    }
}