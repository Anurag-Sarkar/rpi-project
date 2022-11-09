from flask import Flask,render_template,request,redirect,url_for,session
from flask_socketio import SocketIO,send,emit
from pymongo import MongoClient,ReturnDocument
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import adafruit_fingerprint
import time
import serial

uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

#---------------LIBRAREIS--------------------
def enroll_finger(location):
    """Take a 2 finger images and template it, then store in 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...", end="")
        else:
            print("Place same finger again...", end="")

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

@app.route("/attendence")
def index():
    
    if "user" in session:
        x = datetime.datetime.now()
        date = x.strftime("%d-%m-%Y")
        user = attendence.find({"date":date})
        print(user)
        for i in user:
            print(i)
        return render_template("attendence.html",data=user)
    else:
        return redirect("/")


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

@app.route("/entry",methods=["POST"])
def enter():
    n = request.form["name"]
    x = datetime.datetime.now()
    date = x.strftime("%d-%m-%Y")
    time = x.strftime("%H:%M")
    check = attendence.find_one({"name":n,"date":date})
    print(check)
    presense = user.find_one({"name":n})
    print(presense)
    if not check and presense:
        data = {
            "name":n,
            "entry": time,
            "exit" : "-",
            "date" : date
            }
        attendence.insert_one(data)
    return redirect('/')

@app.route("/exit",methods=["POST"])
def exit():
    n = request.form["name"]
    x = datetime.datetime.now()
    time = x.strftime("%H:%M")    
    check = attendence.find_one({"name":n})
    if check and check["exit"] == "-":
        attendence.find_one_and_update({"name":n},{ '$set': { "exit" : time}},return_document=ReturnDocument.AFTER)
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
    n = request.form["name"]
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
            "fingerprint":id,
            "clg":0,
            "password": password
        }
        user.insert_one(data)
        id = 0
        session["user"] = data["name"]
        return redirect("/attendence")
    else:
        return "user exists"
    # else:
    #     return redirect("/")
@app.route("/personelholiday",methods=["POST"])
def allholiday():
    date = []
    start = request.form["startdate"]
    end = request.form["enddate"]
    print(start,end)
    date.append(start)
    date.append(end)
    print(date)
    print(session["user"])
    return redirect("/holiday")

@socket.on("finger")
def message(data):
    print('received message: ')
    enroll_finger(1)
    socket.emit("hello")

socket.run(app,host="0.0.0.0",port="80",debug=True)