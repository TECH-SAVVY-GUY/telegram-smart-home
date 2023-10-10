import os
import dotenv
dotenv.load_dotenv()

import pyrebase
from config import firebaseConfig

import telebot
from telebot.types import Message
from telebot.types import WebAppInfo
from telebot.types import CallbackQuery
from telebot.types import KeyboardButton
from telebot.types import ReplyKeyboardMarkup
from telebot.types import ReplyKeyboardRemove
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from telebot.custom_filters import TextMatchFilter

bot = telebot.TeleBot(os.getenv('API_TOKEN'), parse_mode="HTML")
WEB_APP = "https://telegram-web-apps-production.up.railway.app/smart-home"

firebase = pyrebase.initialize_app(firebaseConfig).database()

markup = ReplyKeyboardMarkup(resize_keyboard=True)
markup.row(KeyboardButton("My Dashboard 🛡️"))
markup.row(KeyboardButton("Profile 👤"), KeyboardButton("Groups 👨‍👩‍👧‍👦"))

def extractValues(message_text: str):
    rawData, data = message_text.split('\n'), []
    for _ in rawData:
        if "➜" in _:
            data.append(_.split('➜')[-1].strip())
    return data

def createNewGroup(message:Message):

    if message.content_type != "text":
        bot.send_message(message.chat.id, "<i>Invalid input! 🚫</i>")
        bot.register_next_step_handler(callback=createNewGroup,
            message=bot.send_message(message.chat.id,
                "<i>What would you like to name your group?</i>",
                    reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).row(
                        KeyboardButton("Cancel ❌"))))
        return
    
    if message.text == "Cancel ❌":
        bot.send_message(message.chat.id, "<i>Operation cancelled! ❌</i>", 
            reply_markup=markup)
    else:

        if len(message.text) > 15:
            bot.send_message(message.chat.id, "<i>Group name cannot be more than 15 characters! 🚫</i>")
            bot.register_next_step_handler(callback=createNewGroup,
                message=bot.send_message(message.chat.id,
                    "<i>What would you like to name your group?</i>",
                        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).row(
                            KeyboardButton("Cancel ❌"))))
            return

        group = firebase.child("groups").push({
            "name": message.text,
            "creator": message.from_user.id,
            "members": {
                "user_id_1": message.from_user.id,
                "user_id_2": False,
                "user_id_3": False
            }
        })

        currentUserGroups = firebase.child("users").child(message.from_user.id).child("groups").get().val()

        for indx, groupID,  in currentUserGroups.items():
            if not groupID:
                firebase.child("users").child(message.from_user.id).child("groups").update({
                    indx: group["name"]
                })
                break

        bot.send_message(message.chat.id, f"<i>Group created successfully! 🎉\n\
            \nGroup ID ➜ <code>{group['name']}</code></i>", reply_markup=markup)

def pairDevice(message:Message, deviceID:str, groupID):

    if message.content_type != "text":
        bot.send_message(message.chat.id, "<i>Invalid input! 🚫</i>")
        bot.register_next_step_handler(callback=pairDevice,
            message=bot.send_message(message.chat.id,
                "<i>Give a name for this device 👉🏻</i>",
                    reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).row(
                        KeyboardButton("Cancel ❌"))))
        return
    
    if message.text == "Cancel ❌":
        bot.send_message(message.chat.id, "<i>Operation cancelled! ❌</i>", 
            reply_markup=markup)
    else:

        if len(message.text) > 15:
            bot.send_message(message.chat.id, "<i>Device name cannot be more than 15 characters! 🚫</i>")
            bot.register_next_step_handler(callback=createNewGroup,
                message=bot.send_message(message.chat.id,
                    "<i>Give a name for this device 👉🏻</i>",
                        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).row(
                            KeyboardButton("Cancel ❌"))))
            return

        if not groupID:
            firebase.child("users").child(message.from_user.id).child(
                "devices").child(deviceID).set(message.text)
            bot.send_message(message.chat.id, f"<i>Device added successfully! 🎉\n\
                \nDevice ID ➜ <code>{deviceID}</code></i>", reply_markup=markup)            
        else:
            firebase.child("groups").child(groupID).child(
                "devices").child(deviceID).set(message.text)
            bot.send_message(message.chat.id, f"<i>Device added successfully! 🎉\n\
                \nDevice ID ➜ <code>{deviceID}</code>\n\
                \nGroup ID ➜ <code>{groupID}</code></i>", reply_markup=markup)

def joinGroup(message:Message):

    if message.content_type != "text":
        bot.send_message(message.chat.id, "<i>Invalid input! 🚫</i>")
        bot.register_next_step_handler(callback=joinGroup,
            message=bot.send_message(message.chat.id, "<i>Enter the group ID 👉🏻</i>",
                reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton("Cancel ❌"))))
        return
    
    if message.text == "Cancel ❌":
        bot.send_message(message.chat.id, "<i>Operation cancelled! ❌</i>", 
            reply_markup=markup)    
    else:
        groupID = message.text
        group = firebase.child("groups").child(groupID).get().val()

        if group is None:
            bot.send_message(message.chat.id, "<i>Invalid group ID! 🚫</i>")
            bot.register_next_step_handler(callback=joinGroup,
                message=bot.send_message(message.chat.id, "<i>Enter the group ID 👉🏻</i>",
                    reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton("Cancel ❌"))))
            return
        else:
            members = group['members']

            if message.from_user.id in members.values():
                bot.send_message(message.chat.id, "<i>You have already joined this group! 🚫</i>")
                return

            for indx, memberID in members.items():
                
                if not memberID:
                    firebase.child("groups").child(
                        groupID).child("members").update({indx: message.from_user.id})
                    bot.send_message(message.chat.id, f"<i>Group joined successfully! 🎉\n\
                        \nGroup ID ➜ <code>{groupID}</code></i>", reply_markup=markup)
                    break
            else:
                bot.send_message(message.chat.id, "<i>Group is full! 🚫</i>")
                bot.register_next_step_handler(callback=joinGroup,
                    message=bot.send_message(message.chat.id, "<i>Enter the group ID 👉🏻</i>",
                        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton("Cancel ❌"))))
                return

@bot.message_handler(commands=["start"])
def start(message:Message):
    bot.send_message(message.chat.id,
        "<i>Hey there! Welcome to the world of IOT! 🔥\n\
        \nDo you want to make your home smart? Click on the button to get started! 👇🏻</i>",
            reply_markup=InlineKeyboardMarkup().row(
                InlineKeyboardButton("Let's explore! 🚂", callback_data="start")))

@bot.message_handler(func=lambda message: message.via_bot)
def newDevice(message: Message):

    isMyBot = message.via_bot.id == bot.get_me().id

    if isMyBot:

        if message.text.startswith("📢 Device Pairing Request!"):
            
            values = extractValues(message.text)
            if len(values) > 1:
                deviceID, groupID = values
            else:   deviceID, groupID = values[0], None

            bot.send_message(message.chat.id, f"<i>Do you want to pair with this device?\n\
                \nDevice ID ➜ <code>{deviceID}</code></i>",
                    reply_markup=InlineKeyboardMarkup().row(
                        InlineKeyboardButton("Yes ✅", callback_data=f"pairDevice:{deviceID}:{groupID}"),
                        InlineKeyboardButton("No ❌", callback_data="cancelPairing")))

@bot.message_handler(chat_types=['private'], text=["My Dashboard 🛡️"])
def myDashboard(message: Message):
    
    bot.send_message(message.chat.id, "<i>Control your smart appliances below 👇🏻</i>",
        reply_markup=InlineKeyboardMarkup(row_width=1).add(*[
                InlineKeyboardButton("Open Dashboard 🛡️", web_app=WebAppInfo(WEB_APP + f"/dashboard?userID={message.from_user.id}")),
                InlineKeyboardButton("Add New Device 💡", callback_data='addNewDevice'),
            ]))

@bot.message_handler(chat_types=['private'], text=["Profile 👤"])
def myProfile(message: Message):
    
    bot.send_message(message.chat.id,
        "<i>Update your profile below 👇🏻</i>",
            reply_markup=InlineKeyboardMarkup().row(
                InlineKeyboardButton(text="Edit Profile ✏️",
                    web_app=WebAppInfo(WEB_APP + "/setMyProfile"))))

@bot.message_handler(chat_types=['private'], text=["Groups 👨‍👩‍👧‍👦"])
def myGroups(message: Message):
    
    currentUserGroups, buttons = firebase.child("users").child(
        message.from_user.id).child("groups").get().val(), []

    inlineMarkup = InlineKeyboardMarkup(row_width=1)

    for indx, groupID in currentUserGroups.items():
        if groupID:
            groupName = firebase.child("groups").child(groupID).child("name").get().val()
            buttons += [InlineKeyboardButton(groupName, callback_data=f"manageGroup:{groupID}")]

    inlineMarkup.add(*buttons)
    inlineMarkup.row(
        InlineKeyboardButton(text="Create new group 👨‍👩‍👧‍👦", callback_data="createNewGroup"),
        InlineKeyboardButton(text="Join a Group 👥", callback_data="joinGroup"),
    )

    bot.send_message(message.chat.id,
        "<i>Manage your groups below 👇🏻</i>", reply_markup=inlineMarkup)

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call:CallbackQuery): 

    data = call.data
    userID = call.from_user.id
    chatID = call.message.chat.id
    msgID = call.message.message_id

    if data == "start":

        if firebase.child("users").child(userID).get().val() is None:

            firebase.child("users").child(userID).set(
                {
                    "name": False,
                    "email": False,
                    "groups": {
                        "group_1": False,
                        "group_2": False,
                        "group_3": False,
                    }
                }
            )

        bot.delete_message(chatID, msgID)
        bot.send_message(chatID, "<i>What would you like to do?</i>", reply_markup=markup)
    
    elif data == "addNewDevice":
        bot.send_message(chatID,
            "<i>In order to add a device, make sure to configure the Wi-Fi settings on your device first!\n\
                \nScan the QR on your device below 👇🏻</i>",
                    reply_markup=InlineKeyboardMarkup().row(
                        InlineKeyboardButton("Scan QR Code", web_app=WebAppInfo(WEB_APP + f"/addNewDevice?groupID=None"))))
        
    elif data == "createNewGroup":

        userGroupsRef = firebase.child("users").child(userID).child("groups")

        groups = userGroupsRef.get().val()

        cuurentGroups = sum(1 for is_member in groups.values() if is_member)

        if cuurentGroups >= 3:

            bot.answer_callback_query(call.id, show_alert=True,
                text="You can create a maximum of 3 groups! ⚠️")
        
        else:

            bot.register_next_step_handler(callback=createNewGroup,
                message=bot.send_message(chatID,
                    "<i>What would you like to name your group?</i>",
                        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).row(
                            KeyboardButton("Cancel ❌"))))

    elif data == "cancelPairing":

        bot.edit_message_text("<i>Operation cancelled! ❌</i>", chatID, msgID)

    elif data.startswith("pairDevice"):

        _0, deviceID, groupID = data.split(":")

        if groupID == "None":

            if firebase.child('users').child(userID).child(
                'devices').child(deviceID).get().val() is not None:
                bot.edit_message_text(chat_id=chatID, message_id=msgID,
                    text="<i>You have already paired with this device! 🚫</i>")
                return

            bot.register_next_step_handler(bot.edit_message_text(
                "<i>Give a name for this device 👉🏻</i>", chatID, msgID), pairDevice, deviceID, None)
            
        else:

            if firebase.child('groups').child(groupID).child(
                'devices').child(deviceID).get().val() is not None:
                bot.edit_message_text(chat_id=chatID, message_id=msgID,
                    text="<i>You have already paired with this device! 🚫</i>")
                return

            bot.register_next_step_handler(bot.edit_message_text(
                "<i>Give a name for this device 👉🏻</i>", chatID, msgID), pairDevice, deviceID, groupID)
                        
    elif data.startswith("manageGroup"):
        
        groupID, buttons = data.split(":")[-1], []
        group = firebase.child("groups").child(groupID).get().val()

        buttons += [InlineKeyboardButton("Add Device 💡", callback_data=f"addDeviceToGroup:{groupID}")]
        if int(group['creator']) == userID:
            buttons += [InlineKeyboardButton("Delete Group 🗑️",
                callback_data=f"deleteGroup:{groupID}")]

        numberOfMembers = sum(1 for is_member in group['members'].values() if is_member)

        bot.edit_message_text(chat_id=chatID, message_id=msgID,
            text=f"<i>Group ID ➜ <code>{groupID}</code>\n\
                \nGroup Name ➜ <code>{group['name']}</code>\n\
                \nGroup Capacity ➜ <code>{numberOfMembers}/3</code></i>",
                    reply_markup=InlineKeyboardMarkup(row_width=1).add(*buttons))
        
    elif data.startswith("deleteGroup"):
            
        groupID = data.split(":")[-1]
        firebase.child("groups").child(groupID).remove()

        groups = firebase.child("users").child(userID).child("groups").get().val()

        for indx, joinedGroupId in groups.items():
            if groupID == joinedGroupId:
                firebase.child("users").child(userID).child("groups").update({indx: False})
                break

        bot.edit_message_text(chat_id=chatID, message_id=msgID,
            text="<i>Group deleted successfully! 🎉</i>")

    elif data.startswith("addDeviceToGroup"):
            
        groupID = data.split(":")[-1]
    
        bot.edit_message_text(chat_id=chatID, message_id=msgID,
            text="<i>Scan the QR on your device below 👇🏻</i>",
                reply_markup=InlineKeyboardMarkup().row(
                    InlineKeyboardButton("Scan QR Code",
                        web_app=WebAppInfo(WEB_APP + F"/addNewDevice?groupID={groupID}"))))

    elif data == "joinGroup":

        bot.register_next_step_handler(callback=joinGroup,
            message=bot.send_message(chatID, "<i>Enter the group ID 👉🏻</i>",
                reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton("Cancel ❌"))))

if __name__ == "__main__":

    print(f'@{bot.get_me().username} is online! 🤖')
    bot.add_custom_filter(TextMatchFilter())
    bot.infinity_polling(skip_pending=True)