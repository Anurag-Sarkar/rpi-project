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

lcd.message = "Welcome Asshole"
