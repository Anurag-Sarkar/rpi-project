const socket = io();


document.querySelector("#left").addEventListener("click",data=>{
    socket.emit("getdata",nam=data.target.id )
    console.log(data.target.id)
    document.querySelector("#right").style.display = "block"
    
})
socket.on("after",function(data){
    console.log(data.data)
    document.querySelector("#details h2").textContent = data.data.name
    document.querySelector("#details #avg #avgtime").textContent = data.data.avg
    document.querySelector("#details #avg #tw").textContent = data.data.totaltime
    document.querySelector("#details #holi #th").textContent = data.data.holiday
    document.querySelector("#details #holi #tl").textContent = data.data.late
    clutter = ""
    data.data.attendence.forEach(deta=>{
        stuff = `<div id="dets">
        <p>${deta.date}</p>
                    <p>${deta.entry}</p>
                    <p>${deta.exit}</p>
                    </div>`
        clutter += stuff
        document.querySelector("#last").innerHTML = clutter

    })


})