// ********************************************************************
//    * Author: 2024 Jingdi Lei (@https://github.com/kyrieLei)#}
// ********************************************************************

const socket=new WebSocket("ws://localhost:8100")

const faceReg=document.getElementById('faceReg')
const faceSave=document.getElementById('faceSaved')
const faceLoad=document.getElementById('faceLoad')

faceReg.addEventListener('click',()=>{
    socket.send(JSON.stringify({action:'r'}));
});

faceSave.addEventListener('click',()=>{
    socket.send(JSON.stringify({action:'s'}));
});

faceLoad.addEventListener('click',()=>{
    socket.send(JSON.stringify({action:'q'}));
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
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        canvas.toBlob(function(blob) {
            if (socket.readyState === WebSocket.OPEN) {
                socket.send(blob);
            }
        }, 'image/jpeg', 0.9); // JPEG格式，质量为0.9
    }, 1000 / 30); // 假设30fps
})
.catch((error)=>{
    socket.send(JSON.stringify({action:"ERROR"}))
})