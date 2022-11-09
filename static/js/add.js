var socket = io()
socket.connect("http://192.168.29.249/add")
console.log("hello")
document.querySelector("#finger").addEventListener("click",(data)=>{
    socket.emit("finger",{"h":"hello","a":"sex"})
})
socket.on('pass', function() {
    document.querySelector("#finger").textContent = "Added"
    document.querySelector("#finger").style.backgroundColor = "rgb(0, 255, 55)"
    document.querySelector("#finger").style.color = "black"
    console.log("again finger")
});
socket.on('fail', function() {
    document.querySelector("#finger").textContent = "Retry"
    document.querySelector("#finger").style.backgroundColor = "rgb(255, 0, 0)"
    document.querySelector("#finger").style.color = "white"

    console.log("not finger")
});
socket.on('again', function() {
    document.querySelector("#finger").textContent = "Place Again"
    document.querySelector("#finger").style.backgroundColor = "rgb(255, 255, 0)"
    document.querySelector("#finger").style.color = "black"
    console.log("not finger")
});