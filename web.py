from flask import Flask,render_template,request,redirect,url_for,session
from flask_socketio import SocketIO,send,emit
from pymongo import MongoClient,ReturnDocument
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import adafruit_fingerprint
import time
import serial
import RPi.GPIO as GPIO
state = 0
print(GPIO.VERSION)
GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)



uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
identitiy = 0
global identity
#---------------LIBRAREIS--------------------
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
        else:
            print("Place same finger again...", end="")
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
GPIO.add_event_detect(26, GPIO.FALLING, callback=print_f, bouncetime=300)



app = Flask(__name__)
app.config["SECRTE"] = "secret"
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
socket = SocketIO(app)
print("Connection to mongodb")

client = MongoClient("mongodb+srv://anurag:1@cluster0.fqzjmis.mongodb.net/?retryWrites=true&w=majority")

db = client["attendence"]
user = db["user"]
attendence = db["attendence"]

@app.route("/attendence")
def index():
    alluser = user.find({})
    for i in alluser:
        print(i)
    x = datetime.datetime.now()
    date = x.strftime("%d-%m-%Y")
    s = attendence.find({"date":date})
    use = []
    for i in s:
        use.append(i)
    print(use)
    return render_template("attendence.html",data=use)

@app.route("/",methods=["GET"])
def login():
    if "user" in session:
       return redirect("/attendence")
    else:
       return render_template("login.html")

@app.route("/loginuser",methods=["POST"])
def loginuser():
    name = request.form["name"]
    pwsd = request.form["password"]
    userdata = user.find_one({"name":name}) 
    if userdata:
        if check_password_hash(userdata["password"],pwsd):
            session["user"] = userdata["name"]
            print(userdata["password"])
            return redirect("/attendence")
        
        else:
            print("hellloo")
            emit("wrong")
            return redirect("/")
    else:
        return redirect("/")

@app.route("/logout",methods=["GET"])
def logout():
    session.pop("user", None)
    return redirect("/")

@app.route("/entry",methods=["GET"])
def enter():
    if get_fingerprint():
        print("Detected #", finger.finger_id, "with confidence", finger.confidence)
        iden = (int(finger.finger_id)*169691)+169691
        cu = user.find_one({"fingerprint": iden})
        print(cu,"user found")
        if cu:
            x = datetime.datetime.now()
            date = x.strftime("%d-%m-%Y")
            times = x.strftime("%H:%M")
            check = attendence.find_one({"name":cu["name"]},{"date":date})
            now = datetime.datetime.now()
            today = now.replace(hour=10, minute=30, second=0, microsecond=0)
            if x > today:
                print("Came late")
                lates = cu["defaultedDays"]
                lates +=1
                print()
                user.find_one_and_update({"name":cu["name"]},{ '$set': { "defaultedDays" : lates}},return_document=ReturnDocument.AFTER)
                remark = "late"
            if not check:
                print("found user")
                data = {
                    "name":cu["name"],
                    "date":date,
                    "time":times,
                    "exit":"-",
                    "remark":remark
                }
                attendence.insert_one(data)
            else:
                print("already entered")
        else:
            print("user not found")
    else:
        print("FUCK YOU")
    return redirect('/attendence')

@app.route("/exit",methods=["GET"])
def exit():
    if get_fingerprint():
        iden = (int(finger.finger_id)*169691)+169691
        cu = user.find_one({"fingerprint": iden})
        n = cu["name"]
        x = datetime.datetime.now()
        time = x.strftime("%H:%M")    
        date = x.strftime("%d-%m-%Y")
        check = attendence.find_one({"name":n})
        if check and check["date"] == date and check["exit"] == "-":
            attendence.find_one_and_update({"name":n},{ '$set': { "exit" : time}},return_document=ReturnDocument.AFTER)
        else:
            print("user exited")
    else:
        print("FUCK YOU")
    return redirect('/')

@app.route("/add",methods=["GET"])
def add():
    # if "user" in session:
    return render_template("add.html")
    # else:
        # return redirect("/")

@app.route("/holiday",methods=["GET"])
def holiday():
    if "user" in session:
        return render_template("holiday.html")
    else:
        return redirect("/")

@app.route("/addmember",methods=["POST"])
def addmember():
    # if "user" in session:
    global identity
    print(identity)
    n = request.form["name"].lower()
    p = request.form["password"]
    print(id)
    print(n)
    check_user = user.find_one({"name":n})
    if not check_user:
        password = generate_password_hash(p)
        data = {
            "name":n,
            "defaultedDays":0,
            "holidays":0,
            "dates":[],
            "fingerprint":identity,
            "clg":0,
            "password": password
        }
        user.insert_one(data)
        identity = 0
        session["user"] = data["name"]
        return redirect("/attendence")
    
    else:
        return "user exists"
    # else:
    #     return redirect("/")
@app.route("/personelholiday",methods=["POST"])
def allholiday():
    date = []
    start = datetime.datetime.strptime(request.form["startdate"],"%Y-%m-%d")
    end = datetime.datetime.strptime(request.form["enddate"],"%Y-%m-%d")
    skip = datetime.timedelta(days=1)
    print(session["user"])
    loggedinuser = user.find_one({"name":session["user"]})
    addeddates = loggedinuser["dates"]
    for i in addeddates:
        print(i,type(i))
    # while(start <= end):
    #     print(start.strftime("%d-%m-%Y"),end="\n")
    #     if start not in addeddates:
    #         user.find_one_and_update({"name":session["user"]},{'$push': {'dates': start.strftime("%d-%m-%Y")}},return_document=ReturnDocument.AFTER)
    #     else:
    #         print("date exists")
    #     start += skip
    # return redirect("/holiday")
@app.route("/deleteall")
def delete():
    finger.read_templates()
    print(finger.templates)
    for i in finger.templates:
        print(i)
        finger.delete_model(i)
    return redirect("/add")
     

         


@socket.on("finger")
def message(data):
    global identity
    list = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,300]
    finger.read_templates()
    print(finger.templates)
    for i in list:
        if not i in finger.templates:
            identity = (i*169691)+169691
            print(i)
            break
    print('received message: ')
    print(identity)
    if not get_fingerprint():
        print("no finger found. adding....")
        if enroll_finger(i): 
            print("Add fingerprint------------------------------")   
            socket.emit("pass")
        else:    
            print("Cant add fingerprint----------------------------")   
            socket.emit("fail")
    else:
        socket.emit("fingerexists")

socket.run(app,host="192.168.29.7",port="80",debug=True)



