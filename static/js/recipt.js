function updatePrice(){
    var gt = 0
    document.querySelectorAll("#price").forEach((e)=>{
        var total = e.textContent
        var total = total.replace(",","")
        total = total.split(".")[0]
        gt = Number(total) + gt
        
    })
    gt = String(gt)
    index = (gt.length-3)
    gt = gt.slice(0,index)+","+gt.slice(index)
    gt = gt + ".00"
    
    document.querySelector("#gt").textContent = gt
}
updatePrice()

document.querySelectorAll("#course_name").forEach((data)=>{
    data.addEventListener("change",(e)=>{
        if(e.target.value === "Python"){
            e.path[1].children[1].innerHTML = "5,000.00"
            updatePrice()
        }
        if(e.target.value === "Java"){
            e.path[1].children[1].innerHTML = "5,500.00"
            updatePrice()
        }
        if(e.target.value === "Registration"){
            e.path[1].children[1].innerHTML = "300.00"
            updatePrice()
        }
        if(e.target.value === "MySQL"){
            e.path[1].children[1].innerHTML = "2,000.00"
            updatePrice()
        }
        if(e.target.value === "CPT"){
            e.path[1].children[1].innerHTML = "10,000.00"
            updatePrice()
        }
        if(e.target.value === "React"){
            e.path[1].children[1].innerHTML = "5,500.00"
            updatePrice()
        }
        if(e.target.value === "C programming"){
            e.path[1].children[1].innerHTML = "3,000.00"
            updatePrice()
        }
        if(e.target.value === "Front-End"){
            e.path[1].children[1].innerHTML = "5,500.00"
            updatePrice()
        }
        if(e.target.value === "Back-end"){
            e.path[1].children[1].innerHTML = "6,000.00"
            updatePrice()
        }
        if(e.target.value === "MERN"){
            e.path[1].children[1].innerHTML = "15,000.00"
            updatePrice()
        }
        // document.querySelector(+" p").textContent = "1000"
    })
})
document.querySelector("#add_course").addEventListener("click",()=>{
    var new_elem =document.createRange().createContextualFragment(`<div id="single_course">
    <select name="course_name" id="course_name">
        <option value="Python">Python</option>
        <option value="Java">Java</option>
        <option value="MySQL">MySQL</option>
        <option value="CPT">CPT</option>
        <option value="React">React</option>
        <option value="MERN">MERN</option>
        <option value="C programming">C programming</option>
        <option value="Front-End">Front-End</option>
        <option value="Back-end">Back-end</option>
        <option value="Registration">Registration</option>
    </select>
    <p id="price">5,000.00</p>
    <i class="ri-close-circle-fill"></i>
</div>`)

    document.querySelector("#course").insertBefore(new_elem,document.querySelector("#add_course"))
})
document.querySelectorAll("i").forEach((data)=>{
    data.addEventListener("click",(e)=>{
        e.path[1].remove()
    })
})