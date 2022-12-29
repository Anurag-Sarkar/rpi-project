const socket = io();


document.querySelector("#left").addEventListener("click",data=>{
    socket.emit("getdata",nam=data.target.id )
    console.log(data.target.id)
    document.querySelector("#right").style.display = "block"
    document.querySelector(".circle").style.display = "block"
    document.querySelector("#all").style.display = "none"
    
})
socket.on("after",function(data){
    console.log(data.data)
    document.querySelector(".circle").style.display = "none"
    document.querySelector("#all").style.display = "block"
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
document.querySelector("#icon i").addEventListener("click",()=>{
    document.querySelector("#overlap").style.left = "0%"
})
document.querySelector("#overlap").addEventListener("click",()=>{
    document.querySelector("#overlap").style.left = "130%"
})