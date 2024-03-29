from flask import Flask,render_template,request,redirect,url_for,session
from flask_socketio import SocketIO,send,emit
from pymongo import MongoClient,ReturnDocument
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import adafruit_fingerprint
import time
import serial
import RPi.GPIO as GPIO
from subprocess import Popen, PIPE
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd
from threading import Timer


time.sleep(5)

state = 0
GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
GPIO.setup(8,GPIO.OUT)
GPIO.output(8, GPIO.HIGH)  # make ledPin output HIGH level to turn on led - Here HIGH TURNS ON LED

pwsd = "sherytheattendence"

uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
identitiy = 0
#---------------LIBRAREIS--------------------


# Modify this if you have a different sized character LCD
lcd_columns = 16
lcd_rows = 2

# compatible with all versions    of RPI as of Jan. 2019
# v1 - v3B+
lcd_rs = digitalio.DigitalInOut(board.D22)
lcd_en = digitalio.DigitalInOut(board.D17)
lcd_d4 = digitalio.DigitalInOut(board.D25)
lcd_d5 = digitalio.DigitalInOut(board.D24)
lcd_d6 = digitalio.DigitalInOut(board.D23)
lcd_d7 = digitalio.DigitalInOut(board.D18)


# Initialise the lcd class
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
                                      lcd_d7, lcd_columns, lcd_rows)
lcd.clear()

lcd.message = "Welcome to\nSHERYIANS"


def defaultt():
    lcd.clear()
    lcd.message = 'Press The button\nto interact'



list = []
def print_f(pin):
    global list
    list.append(2)
    print(list)
    print(len(list))
    if len(list) > 2:
        enter()
        list = []

def enroll_finger(location):
    """Take a 2 finger images and template it, then store in 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...", end="")
            lcd.clear()
            lcd.message = "Place Your Finger\non sensor"

        else:
            print("Place same finger again...", end="")
            lcd.clear()
            lcd.message = "Place again"
            socket.emit("again")



        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                print("Image taken")
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="")
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Imaging error")
                return False
            else:
                print("Other error")
                return False

        print("Templating...", end="")
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            print("Templated")
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Image too messy")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("Could not identify features")
                lcd.clear()
                lcd.message = "Clean sensor\n or finger"
                t = Timer(10, defaultt)  
                t.start()
 


            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return False

        if fingerimg == 1:
            print("Remove finger")
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    print("Creating model...", end="")
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Created")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("Prints did not match")
        else:
            print("Other error")
        return False

    print("Storing model #%d..." % location, end="")
    i = finger.store_model(location)
    if i == adafruit_fingerprint.OK:
        print("Stored")
    else:
        if i == adafruit_fingerprint.BADLOCATION:
            print("Bad storage location")
        elif i == adafruit_fingerprint.FLASHERR:
            print("Flash storage error")
        else:
            print("Other error")
        return False

    return True
try:
    def get_fingerprint():
        lcd.clear()
        lcd.message = "Place Finger"
        """Get a finger print image, template it, and see if it matches!"""
        print("Waiting for image...")
        while finger.get_image() != adafruit_fingerprint.OK:
            pass
        print("Templating...")
        if finger.image_2_tz(1) != adafruit_fingerprint.OK:
            return False
        print("Searching...")
        if finger.finger_search() != adafruit_fingerprint.OK:
            return False
        return True
except Exception:
    print(Exception)
#---------------LIBRAREIS--------------------

app = Flask(__name__)
app.config["SECRTE"] = "secret"
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
socket = SocketIO(app)
print("Connection to mongodb")
client = MongoClient("mongodb+srv://anurag:1@cluster0.fqzjmis.mongodb.net/?retryWrites=true&w=majority")
db = client["attendence"]
user = db["user"]
attendence = db["attendence"]
recipt = db["recipt"]

lol = user.find_one({"name":"sheryians coding school"})
print("dojo find")
if not lol:
    data = {
        "name":"sheryians coding school",
        "holiday":0,
        "dates":[],
        }
    user.insert_one(data)


@app.route("/")
def red():
    return redirect('/attendence')

@app.route("/attendence")
def index():
    alluser = user.find({})
    today = datetime.datetime.now()   
    today = today.strftime("%d-%m-%Y")
    dojo = user.find_one({"name":"sheryians coding school"})
    dojo_holiday = dojo["dates"]
    for i in alluser:
        if i["name"] != "sheryians coding school": 
            print(today , i["dates"])
            if today in i["dates"]:   
                if today in dojo_holiday:
                    print("removed holiday",i["name"])
                    holiday = i["holiday"]  
                    if holiday > 0:
                        holiday -= 1
                    user.find_one_and_update({"name":i["name"]},{ '$set': { "holiday" : holiday}},return_document=ReturnDocument.AFTER)
                    dates = user.find_one({"name":i["name"]}) 
                    dates = dates["dates"]
                    dates.remove(today)
                    user.find_one_and_update({"name":i["name"]},{ '$set': { "dates" : dates}},return_document=ReturnDocument.AFTER)
                else:
                    print("user added to attendence")
                    data = {
                            "name":i["name"],
                            "date":today,
                            "time":"-",
                            "exit":"-",
                            "remark":"holiday"
                        }
                    present = attendence.find_one({"name":i["name"] , "date":today})
                    print(present)
                    if not present:
                        attendence.insert_one(data) 

        elif today in dojo_holiday:
            data = {
                    "name":"sheryians coding school",
                    "date":today,
                    "time":"-",
                    "exit":"-",
                    "remark":"holiday"
                        }
            present = attendence.find_one({"name":"sheryians coding school","date":today})
            if not present:
                attendence.insert_one(data)    
                

                
            
    x = datetime.datetime.now()
    date = x.strftime("%d-%m-%Y")
    s = attendence.find({"date":date})
    use = []
    for i in s:
        # temp_entry = i["entry"].split(":")
        # if int(temp_entry[0]) > 12:
        #     int(temp_entry[0])-12
        
        use.append(i)
    return render_template("attendence.html",data=use)

@app.route("/entry",methods=["GET"])
def enter():
    
    remark = "normal"
    if get_fingerprint():

        
        print("Detected #", finger.finger_id, "with confidence", finger.confidence)
        iden = (int(finger.finger_id)*169691)+169691
        print(iden)
        cu = user.find_one({"fingerprint": iden})
        if cu:
            x = datetime.datetime.now()
            date = x.strftime("%d-%m-%Y")
            times = x.strftime("%H:%M")
            check = attendence.find_one({"name":cu["name"] ,"date":date})
            now = datetime.datetime.now()
            today_time = now.replace(hour=11, minute=0, second=0, microsecond=0)
            if x > today_time:
                dojo = user.find_one({"name":"sheryians coding school"})
                holidaycheck = dojo["dates"]
                if date in holidaycheck:
                    print("Over time")
                    ot = cu["overtime"]
                    ot +=1
                    user.find_one_and_update({"name":cu["name"]},{ '$set': { "overtime" : ot}},return_document=ReturnDocument.AFTER)
                    remark = "extra"
                else:
                    if not check:
                        print("Came late")
                        lates = cu["defaultedDays"]
                        lates +=1
                        user.find_one_and_update({"name":cu["name"]},{ '$set': { "defaultedDays" : lates}},return_document=ReturnDocument.AFTER)
                        remark = "late"

            if not check:
                print("found user")
                lcd.clear()
                lcd.message = "Welcome...\n" + cu["name"]
                t = Timer(10, defaultt)  
                t.start()
                data = {
                    "name":cu["name"],
                    "date":date,
                    "entry":times,
                    "exit":"-",
                    "remark":remark
                }
                attendence.insert_one(data)



            else:
                print("user aready in work")
                check_holiday = attendence.find_one({"name":cu["name"]})
                if check_holiday["remark"] == "holiday":
                    halfday = cu["halfday"]
                    holiday = cu["holiday"]
                    halfday += 1
                    holiday -= 1
                    user.find_one_and_update({"name":cu["name"]},{ '$set': { "halfday" : halfday }},return_document=ReturnDocument.AFTER)
                    user.find_one_and_update({"name":cu["name"]},{ '$set': { "holiday" : halfday }},return_document=ReturnDocument.AFTER)
                    attendence.find_one_and_update({"name":cu["name"]},{ '$set': { "times" : times}},return_document=ReturnDocument.AFTER)
                    attendence.find_one_and_update({"name":cu["name"]},{ '$set': { "remark" : "halfday"}},return_document=ReturnDocument.AFTER)
                
                elif check and check["date"] == date and check["exit"] == "-" :
                    print("exited")
                    print(date)
                    lol = attendence.find_one_and_update({"name":cu["name"],"date":date},{ '$set': { "exit" : times}})
                    print(lol,"exited data")
                    print(attendence.find_one({"name":cu["name"]}))
                    lcd.clear()
                    lcd.message = "Goodbye\n" + cu["name"]
                    t = Timer(10, defaultt)  
                    t.start()
                else:
                    lcd.message = "You are already\nLogged"
                    t = Timer(10, defaultt)  
                    t.start()

 
        else:
            lcd.clear()
            lcd.message = "You are not\n registers"
            print("user not found")
            t = Timer(10, defaultt)  
            t.start()
    else:
        lcd.clear()
        lcd.message = "Cant recognise\nfingerprint" 
        t = Timer(10, defaultt)  
        t.start()
        print("FUCK YOU")

    return redirect('/attendence',200,{"success":True})

@app.route("/login",methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/loginuser",methods=["POST"])
def loginuser():
    password = request.form["password"]
    if password == pwsd:
        print("welcome admin")
        session["username"] = "JGHKUH^%&dMGR%^&^%IUNTV&#$^RB^IuB(R^&#W%^C"
        return redirect("/admin")
    else:
        return redirect("/login")


@app.route("/logout",methods=["GET"])
def logout():
    session.pop("username",None)
    return redirect("/attendence")

@app.route("/add",methods=["GET"])
def add():
    try:
        if session["username"] == "JGHKUH^%&dMGR%^&^%IUNTV&#$^RB^IuB(R^&#W%^C":
            return render_template("add.html")
        else:
            return redirect("/attendence")
    except Exception as err:
        return redirect("/login")

@app.route("/addmember",methods=["POST"])
def addmember():
    try:
        if session["username"] == "JGHKUH^%&dMGR%^&^%IUNTV&#$^RB^IuB(R^&#W%^C":
            global identitiy
            name = request.form["name"]
            check = user.find_one({"name":name})
            print(check,"this is user details")
            if not check:
                data = {
                    "name":name.title(),
                    "fingerprint":identitiy,
                    "holiday":0,
                    "dates":[],
                    "overtime":0,
                    "defaultedDays":0
                }
                user.insert_one(data)
            else:
                print(identitiy)
                print("USER ALREADY ADDED")
            return redirect("/admin")
        else:
            return redirect("/attendence")
    
    except Exception as err:
        return redirect("/login")
        
@app.route("/holiday",methods=["GET"])
def holiday():
    try:
        if session["username"] == "JGHKUH^%&dMGR%^&^%IUNTV&#$^RB^IuB(R^&#W%^C":
            users = user.find({})
            return render_template("holiday.html",user = users)
        else:
            return redirect("/attendence")
    except Exception as err:
        return redirect("/login")
        

@app.route("/addingholiday",methods=["POST"])
def personalholiday():
    try:
        if session["username"] == "JGHKUH^%&dMGR%^&^%IUNTV&#$^RB^IuB(R^&#W%^C":
            start = datetime.datetime.strptime(request.form["startdate"],"%Y-%m-%d")
            skip = datetime.timedelta(days=1)
            print(request.form["user"])
            user_name = user.find_one({"name":request.form["user"]})
            print(user_name)
            addeddates = user_name["dates"]
            holiday = user_name["holiday"]
            dojo  = user.find_one({"name":"sheryians coding school"})
            dojo_holiday = dojo["dates"]
            end = request.form["enddate"]
            if end == "":
                if start not in dojo_holiday:
                    print(start)
                    holiday += 1
                    user.find_one_and_update({"name":user_name["name"]},{'$push': {'dates': start.strftime("%d-%m-%Y")}},return_document=ReturnDocument.AFTER)
                    user.find_one_and_update({"name":user_name["name"]},{ '$set': { "holiday" : holiday}},return_document=ReturnDocument.AFTER)
            else:
                end = datetime.datetime.strptime(end,"%Y-%m-%d")
                while(start <= end):
                    print(start.strftime("%d-%m-%Y"),type(start.strftime("%d-%m-%Y")),end="\n")
                    if start.strftime("%d-%m-%Y") not in addeddates and start.strftime("%d-%m-%Y") not in dojo_holiday:
                        print("adding dates")
                        holiday += 1
                        user.find_one_and_update({"name":user_name["name"]},{ '$set': { "holiday" : holiday}},return_document=ReturnDocument.AFTER)
                        user.find_one_and_update({"name":user_name["name"]},{'$push': {'dates': start.strftime("%d-%m-%Y")}},return_document=ReturnDocument.AFTER)
                    else:
                        print("date exists")
                    start += skip
            return redirect("/holiday")
        else:
            return redirect("/attendence")
    except Exception as err:
        return redirect("/login")
        
@app.route("/deleteall")
def delete():
    try:
        if session["username"] == "JGHKUH^%&dMGR%^&^%IUNTV&#$^RB^IuB(R^&#W%^C":
            finger.read_templates()
            print(finger.templates)
            for i in finger.templates:
                print(i)
            return redirect("/add")
        else:
            return redirect("/attendence")
    except Exception as err:
        return redirect("/login")
            
@app.route("/delete")
def deleteone():
    try:
        if session["username"] == "JGHKUH^%&dMGR%^&^%IUNTV&#$^RB^IuB(R^&#W%^C":
            l = [4,5,8,9,10,11,13]
            for i in range(17):
                if i not in l:
                    
                    # finger.delete_model(i)
                    print(i)
            print(finger.templates)
            return redirect("/admin")
        else:
            return redirect("/attendence")
    except Exception as err:
        return redirect("/login")
            


@app.route("/deleteholiday")
def deleteholiday():
    try:
        if session["username"] == "JGHKUH^%&dMGR%^&^%IUNTV&#$^RB^IuB(R^&#W%^C":
            logged = user.find_one({"name":session["username"]})
            return render_template("deleteholiday.html",date=logged["dates"])
        else:
            return redirect("/attendence")
    except Exception as err:
        return redirect("/login")
        


@app.route("/olddata")
def olddata():
    try:
        if session["username"] == "JGHKUH^%&dMGR%^&^%IUNTV&#$^RB^IuB(R^&#W%^C":
            today = datetime.datetime.now()
            data = []
            for i in range(30):
                people = []
                d = today - datetime.timedelta(days = i)
                found = attendence.find({"date":d.strftime("%d-%m-%Y")})
                people.append(d.strftime("%d-%m-%Y"))
                for i in found:
                    people.append(i)
                data.append(people)
            return render_template("data.html",deta=data)
        else:
            return redirect("/attendence")
    except Exception as err:
        return redirect("/login")
        
@app.route("/profile")
def profile ():
    users = user.find({})
    return render_template("profile.html",user = users)

@app.route("/admin")
def admin():
    try:
        print(session["username"])
        if session["username"] == "JGHKUH^%&dMGR%^&^%IUNTV&#$^RB^IuB(R^&#W%^C":
            users = user.find({})
            return render_template("admin.html",user = users)
        else:
            return redirect("/login")
    except Exception as err:
        return redirect("/login")
#--------------------------------------RECIPT-----------------------------------------------
@app.route("/recipt")
def recipt():
    return render_template("recipt.html")






#---------------------------------------SOCKET IO---------------------------------------------
@socket.on("getdata")
def getname(data):
    print(data)
    u = user.find_one({"name":data})
    base = datetime.datetime.today()
    days = int(base.strftime("%d"))
    date_list = [base - datetime.timedelta(days=x) for x in range(days)]
    time_sum = datetime.timedelta()
    avg_time = datetime.timedelta()
    last = []
    for i in date_list:
        print(i.strftime("%d-%m-%y"))
        user_data = attendence.find_one({"name":data,"date":i.strftime("%d-%m-%Y")})
        # user_data = attendence.find_one({"name":data})
        print(user_data)
        if user_data:
            if user_data["remark"] == "holiday":
                attend = {
                "name":u["name"],
                "date":i.strftime("%d-%m-%y"), 
                "entry":"holiday",
                "exit":"holiday"
                    }
                last.append(attend)
            else:    

                attend = {
                    "name":u["name"],
                    "date":i.strftime("%d-%m-%y"), 
                    "entry":user_data["entry"],
                    "exit":user_data["exit"]
                }
                last.append(attend)

                if user_data["exit"] != "-":
                    t = datetime.datetime.strptime(user_data["exit"],"%H:%M") - datetime.datetime.strptime(user_data["entry"],"%H:%M")
                    h,m,s = str(t).split(":")
                    d = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))
                    time_sum += d        

                    hour,minute = str(user_data["entry"]).split(":")
                    av = datetime.timedelta(hours=int(hour), minutes=int(minute))
                    avg_time += av
        else:
            attend = {
                "name":u["name"],
                "date":i.strftime("%d-%m-%y"), 
                "entry":"na",
                "exit":"na"
            }
            last.append(attend)
    plate = {
        "date" : "Date",
        "entry" : "Entry",
        "exit" : "Exit"
    }
    last.insert(0,plate)
    total_time = (str(time_sum.days*24 + time_sum.seconds//3600) + ":" + str((time_sum.seconds % 3600)//60)) 
    avg_time = str(avg_time/4)
    usr = {
        "name":u["name"].title(),
        "totaltime":str(total_time),
        "holiday":u["holiday"],
        "late":u["defaultedDays"],
        "avg":avg_time[0:-3],
        "attendence":last
    }
    emit('after',  {'data':usr,"sex":"hi"})

@socket.on("finger")
def message(data):
    global identitiy
    list = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,300]
    finger.read_templates()
    print(finger.templates)
    for i in list:
        if not i in finger.templates:
            identitiy = (i*169691)+169691
            print(i)
            break
    print('received message: ')
    print(identitiy)
    if not get_fingerprint():
        print("no finger found. adding....")
        if enroll_finger(i): 
            print("Add fingerprint------------------------------") 
            lcd.clear() 
            lcd.message = "Added Fingerprint"
            t = Timer(10, defaultt)  
            t.start()
            socket.emit("pass")
        else:    
            print("Cant add fingerprint----------------------------")   
            socket.emit("fail")
    else:
        lcd.clear()
        lcd.message = "Finger Exists\nPlace Another finger"
        t = Timer(10, defaultt)  
        t.start()
        socket.emit("fingerexists")



socket.run(app,host="192.168.29.7",port="80",debug=False)



