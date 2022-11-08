document.querySelector("#main #nav i").addEventListener("click",(data)=>{
    console.log("Hello")
    document.querySelector("#overlay").style.left = "0%"
})
document.querySelector("#overlay i").addEventListener("click",(data)=>{
    console.log("Hello")
    document.querySelector("#overlay").style.left = "100%"
})

document.querySelector("#button:nth-child(1)").addEventListener("click",(data)=>{
    window.location.href = '/add'; 
    console.log("hheh")
    
})
document.querySelector("#holiday").addEventListener("click",(data)=>{
    console.log("hheh")
    window.location.href = '/holiday'; 

})
