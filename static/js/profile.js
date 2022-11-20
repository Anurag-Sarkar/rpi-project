const socket = io();


document.querySelector("#user").addEventListener("change",data=>{
    console.log(data.target.value)
    socket.emit("getdata",nam=data.target.value)
    document.querySelector("#status").textContent = "LOADING..."
    
})
console.log("hello")

socket.on("after",function(data){
    document.querySelector("#status").textContent = ""
    document.querySelector("#right").style.display = "block"
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