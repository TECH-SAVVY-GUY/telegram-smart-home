import re
import os
import dotenv
dotenv.load_dotenv()
from pprint import pprint

import pyrebase
from config import firebaseConfig

from flask import Flask
from flask import request
from flask import redirect
from flask import render_template

import telebot
from telebot.types import InputMediaPhoto
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from telebot.types import InlineQueryResultPhoto
from telebot.types import InputTextMessageContent
from telebot.types import InlineQueryResultArticle

from telebot.util import parse_web_app_data
from telebot.util import validate_web_app_data


API_TOKEN = os.getenv("API_TOKEN")

app = Flask(__name__, static_url_path="/static")
bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")
firebase = pyrebase.initialize_app(firebaseConfig).database()

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if request.method == "POST":
        1
    


    devices, userID = {}, request.args.get("userID")

    user = firebase.child('users').child(userID).get().val()

    groups = user["groups"]

    personalDevices = user["devices"]

    for deviceID in personalDevices:
        devices[deviceID] = {
            'name' : personalDevices[deviceID],
            'groups' : ['Personal']
        }

    for idx in groups:
        if groups[idx]:
            groupID = groups[idx]
            group = firebase.child('groups').child(groupID).get().val()

            groupDevices = group["devices"]

            for deviceID in groupDevices:
                if deviceID not in devices:
                    devices[deviceID] = {
                        'name' : groupDevices[deviceID],
                        'groups' : [group["name"]]
                    }
                else:
                    devices[deviceID]['groups'] += [group["name"]]

    pprint(devices)

    for deviceID in devices:
        device = devices[deviceID]
        device["groups"] = ", ".join(device["groups"])

    return render_template('dashboard.html', devices=devices)


@app.route("/setMyProfile", methods=["GET", "POST"])
def setProfile():
    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")

        initData = request.form.get("initData")

        isValid = validate_web_app_data(bot.token, initData)

        if isValid:

            web_app_data = parse_web_app_data(bot.token, initData)

            query_id = web_app_data["query_id"]

            firebase.child("users").child(
                int(web_app_data['user']['id'])).update(
                    {"name": name, "email": email,}
            )

            bot.answer_web_app_query(query_id, InlineQueryResultArticle(
                id=query_id, title="PROFILE UPDATED ✅",
                input_message_content=InputTextMessageContent(
                    "<i>Profile updated! ✅</i>", parse_mode="HTML")))

        return "Response <200>"

    else:
        return render_template("setProfile.html")

@app.route("/addNewDevice", methods=["GET", "POST"])
def addNewDevice():

    if request.method == "POST":

        rawData = request.json
        groupID = rawData["groupID"]
        initData = rawData["initData"]

        isValid = validate_web_app_data(API_TOKEN, initData)

        if isValid:

            web_app_data = parse_web_app_data(API_TOKEN, initData)

            query_id = web_app_data["query_id"]

            deviceID = rawData["qr"]

            if firebase.child("devices").child(deviceID).get().val() == None:
                bot.answer_web_app_query(query_id, InlineQueryResultArticle(
                    id=query_id, title="INVALID DEVICE ID! 🚫",
                    input_message_content=InputTextMessageContent(
                        "<i>Invalid device ID! 🚫</i>", parse_mode="HTML")))
            else:
                message_text = f"<i>📢 Device Pairing Request!\n\
                        \nDevice ID ➜ <code>{deviceID}</code></i>"
                if groupID != "None":
                    message_text += f"\n\n<i>Group ID ➜ <code>{groupID}</code></i>"

                bot.answer_web_app_query(query_id, InlineQueryResultArticle(
                    id=query_id, title="DEVICE PAIRING REQUEST 🔥",
                    input_message_content=InputTextMessageContent(message_text, parse_mode="HTML")))
        
    return render_template('addNewDevice.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0')



    # pprint(devices)