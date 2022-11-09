var socket = io()
socket.connect("http://192.168.29.249/add")
console.log("hello")
document.querySelector("#finger").addEventListener("click",(data)=>{
    socket.emit("finger",{"h":"hello","a":"sex"})
})
socket.on('pass', function() {
    console.log("added finger")
});
socket.on('pass', function() {
    console.log("not finger")
});