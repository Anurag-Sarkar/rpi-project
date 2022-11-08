from flask import Flask,render_template,request,redirect,url_for,session
from flask_socketio import SocketIO,send,emit
from pymongo import MongoClient,ReturnDocument
from werkzeug.security import generate_password_hash, check_password_hash

import datetime

# lcd_rs        = 22  # Note this might need to be changed to 21 for older revision Pi's.
# lcd_en        = 17
# lcd_d4        = 25
# lcd_d5        = 24
# lcd_d6        = 23
# lcd_d7        = 18
# lcd_backlight = 4

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
# import busio
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint

led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

# uart = busio.UART(board.TX, board.RX, baudrate=57600)

# # If using with a computer such as Linux/RaspberryPi, Mac, Windows with USB/serial converter:
# import serial
# uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)

# # If using with Linux/Raspberry Pi and hardware UART:
import serial
uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)

finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

# ##################################################


# def get_fingerprint():
#     """Get a finger print image, template it, and see if it matches!"""
#     print("Waiting for image...")
#     while finger.get_image() != adafruit_fingerprint.OK:
#         pass
#     print("Templating...")
#     if finger.image_2_tz(1) != adafruit_fingerprint.OK:
#         return False
#     print("Searching...")
#     if finger.finger_search() != adafruit_fingerprint.OK:
#         return False
#     return True


# # pylint: disable=too-many-branches
# def get_fingerprint_detail():
#     """Get a finger print image, template it, and see if it matches!
#     This time, print out each error instead of just returning on failure"""
#     print("Getting image...", end="")
#     i = finger.get_image()
#     if i == adafruit_fingerprint.OK:
#         print("Image taken")
#     else:
#         if i == adafruit_fingerprint.NOFINGER:
#             print("No finger detected")
#         elif i == adafruit_fingerprint.IMAGEFAIL:
#             print("Imaging error")
#         else:
#             print("Other error")
#         return False

#     print("Templating...", end="")
#     i = finger.image_2_tz(1)
#     if i == adafruit_fingerprint.OK:
#         print("Templated")
#     else:
#         if i == adafruit_fingerprint.IMAGEMESS:
#             print("Image too messy")
#         elif i == adafruit_fingerprint.FEATUREFAIL:
#             print("Could not identify features")
#         elif i == adafruit_fingerprint.INVALIDIMAGE:
#             print("Image invalid")
#         else:
#             print("Other error")
#         return False

#     print("Searching...", end="")
#     i = finger.finger_fast_search()
#     # pylint: disable=no-else-return
#     # This block needs to be refactored when it can be tested.
#     if i == adafruit_fingerprint.OK:
#         print("Found fingerprint!")
#         return True
#     else:
#         if i == adafruit_fingerprint.NOTFOUND:
#             print("No match found")
#         else:
#             print("Other error")
#         return False


# # pylint: disable=too-many-statements
def enroll_finger(location):
    """Take a 2 finger images and template it, then store in 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...", end="")
            SocketIO.emit("addfinger",{"data":24})
        else:
            print("Place same finger again...", end="")
            SocketIO.send("againfinger") 


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
                SocketIO.emit("clean")
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


# ##################################################


# def get_num():
#     """Use input() to get a valid number from 1 to 127. Retry till success!"""
#     i = 0
#     while (i > 127) or (i < 1):
#         try:
#             i = int(input("Enter ID # from 1-127: "))
#         except ValueError:
#             pass
#     return i


# while True:
#     print("----------------")
#     if finger.read_templates() != adafruit_fingerprint.OK:
#         raise RuntimeError("Failed to read templates")
#     print("Fingerprint templates:", finger.templates)
#     print("e) enroll print")
#     print("f) find print")
#     print("d) delete print")
#     print("----------------")
#     c = input("> ")

#     if c == "e":
#         enroll_finger(get_num())
#     if c == "f":
#         if get_fingerprint():
#             print("Detected #", finger.finger_id, "with confidence", finger.confidence)
#         else:
#             print("Finger not found")
#     if c == "d":
#         if finger.delete_model(get_num()) == adafruit_fingerprint.OK:
#             print("Deleted!")
#         else:
#             print("Failed to delete")

app = Flask(__name__)
app.config["SECRTE"] = "secret"
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

socket = SocketIO(app,cors_allowed_origins="*")
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
    print(n)
    check_user = user.find_one({"name":n})
    if not check_user:
        password = generate_password_hash(p)
        data = {
            "name":n,
            "defaultedDays":0,
            "holidays":0,
            "dates":[],
            "fingerprint":0,
            "clg":0,
            "password": password
        }
        user.insert_one(data)
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
def message():
    if enroll_finger(1):
        socket.send("success")
    else:
        socket.emit("fail")

socket.run(app,host="192.168.29.249",port="80",debug=True)