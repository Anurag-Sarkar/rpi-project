var socket = io()
console.log("hello")
document.querySelector("#finger").addEventListener("click",(data)=>{
    socket.emit("finger")
    console.log("send")
})