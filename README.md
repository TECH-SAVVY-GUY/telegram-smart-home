# *Telegram ➜ [@MySmartyHomeBot 🏠](https://t.me/MySmartyHomeBot)*

This bot allows the users to manage their smart appliances from within Telegram!

**Let's understand the flow of the bot:**

1. The user starts the bot and sets their profile.
   
2. The user can create groups and invite other users to join their group.

3. Users in a group can collectively access the same device.

4. The users can also add devices to their own account.

5. The device is simply a `ESP8266` board connected to some relays.

6. The ESP needs to be configured to access the internet - More info at [esp-smart-client](https://github.com/TECH-SAVVY-GUY/esp-smart-client)

We are using Firebase for the project. Here's the database schema for the bot:

```json
{
  "devices": {
    "device_id_1": {
      "MAC ID": "AA:BB:CC:DD:EE:FF",
      "relays": {
        "relay_1": {
          "name": "Device 1",
          "state": true
        },
        "relay_2": {
          "name": "Device 2",
          "state": false
        },
        "relay_3": {
          "name": "Device 3",
          "state": true
        },
        "relay_4": {
          "name": "Device 4",
          "state": false
        }
      },
      "type": "4-channel"
    },
    "device_id_2": {
      "MAC ID": "AA:11:BB:CC:55:DE",
      "relays": {
        "relay_1": {
          "name": "Device 1",
          "state": true
        }
      },
      "type": "1-channel"
    }
  },
  "groups": {
    "group_id_1": {
      "creator": "user_id_1",
      "devices": {
        "device_id_2": "Group Lights"
      },
      "members": {
        "user_id_1": "user_id_1",
        "user_id_2": "user_id_2",
        "user_id_3": false
      },
      "name": "My Smart Home"
    }
  },
  "users": {
    "user_id_1": {
      "devices": {
        "device_id_1": "Living Room Lights",
      },
      "email": "user1@email.com",
      "groups": {
        "group_1": "group_id_1",
        "group_2": false,
        "group_3": false
      },
      "name": "User Name 1"
    },
    "user_id_2": {
      "email": false,
      "groups": {
        "group_1": false,
        "group_2": false,
        "group_3": false
      },
      "name": false
    }
  }
}
```

Let's understand how the system works all together!

The devices are added to the bot by scanning a code that comes along with it. A sample is given below 👇🏻

![smartyy_page-0001](https://github.com/TECH-SAVVY-GUY/telegram-smart-home/assets/83786816/ff1cabce-6592-4213-8f2b-b4d06f21e75b)

The QR codes are generated based on the MAC Address of the `ESP-Client`

Each `ESP-Client` listens to a server endpoint which monitors the status change in it's database. Whenever a change is detected, the `ESP-Client` sets the respective GPIO Pin to `high (1)` or `low (0)` based on it's state.

Here's a sample circuit diagram for connecting the `ESP-Client` to a 8-channel relay 👉🏻

![image](https://github.com/TECH-SAVVY-GUY/telegram-smart-home/assets/83786816/5c16dd0d-8026-4386-b0c1-a0ec86b4604b)

_**Therefore, this system can be integrated with any existing devices by connecting it to the respective relays.**_

**If you like this project, kindly give a star! ⭐**

**Contributions are welcome! 😇**

