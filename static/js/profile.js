document.querySelector("#user").addEventListener("change",data=>{
    console.log(data.target.value)
    socket.emit("getdata",nam=data.target.value )

})
console.log("hello")

socket.on("after",function(data){
    console.log(data.data)
})