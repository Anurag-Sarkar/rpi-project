var socket = io()
socket.connect("http://192.168.29.249/add")
console.log("hello")
document.querySelector("#finger").addEventListener("click",(data)=>{
    socket.emit("finger",{"h":"hello","a":"sex"})
})
socket.on('hello', function() {
    console.log("hello from backend")
});