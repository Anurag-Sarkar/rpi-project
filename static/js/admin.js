const socket = io();


document.querySelector("#left").addEventListener("click",data=>{
    socket.emit("getdata",nam=data.target.id )
    console.log(data.target.id)
})
socket.on("returndata",function(data){
    console.log(data)
})