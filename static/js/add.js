var socket = io()
socket.connect("http://192.168.29.249/add")
console.log("hello")
document.querySelector("#finger").addEventListener("click",(data)=>{
    socket.emit("finger",{"h":"hello","a":"sex"})
})
socket.on('pass', function() {
    document.querySelector("#finger").textContent = "Added"
    console.log("added finger")
});
socket.on('fail', function() {
    document.querySelector("#finger").textContent = "Retry"
    console.log("not finger")
});
socket.on('again', function() {
    document.querySelector("#finger").textContent = "Place Finger Again"
    console.log("not finger")
});