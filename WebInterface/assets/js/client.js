const socket=new WebSocket("ws://localhost:8094")

const faceReg=document.getElementById('faceReg')
const faceSave=document.getElementById('faceSaved')

faceReg.addEventListener('click',()=>{
    socket.send(JSON.stringify({action:'r'}));
});

faceSave.addEventListener('click',()=>{
    socket.send(JSON.stringify({action:'s'}));
});

navigator.mediaDevices.getUserMedia({video:true})
.then((stream)=>{
   const videoElement=document.getElementById('videoElement');
   videoElement.srcObject=stream
})
.catch((error)=>{
    socket.send(JSON.stringify({action:"ERROR"}))
})