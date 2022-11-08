var socket = io()
console.log("hello")
document.querySelector("#finger").addEventListener("click",(data)=>{
    socket.emit("finger")
})
socket.on("success",(data)=>{
    console.log("added fingerprint")
})
socket.on("fail",(data)=>{
    console.log("faild fingerprint")
})
socket.on("clean",(data)=>{
    console.log("clean fingerprint")
})
socket.on("addfinger",(data)=>{
    console.log("place finger") 
})
socket.on("againfinger",(data)=>{
    console.log("place finger again")
})