# motioneyeos-discord-notifier
Script for pushing notifications to Discord when a motion is detected on your [MotionEyeOS](https://github.com/ccrisan/motioneyeos/wiki) device

# Credits
Inital version created by [Bluscream](https://github.com/Bluscream) and [IAmOrion](https://github.com/IAmOrion)

Originally copied from here: https://github.com/ccrisan/motioneyeos/issues/1557#issuecomment-399692426 and then modified slightly

# Installation:
- Create a Discord webhook. See [here](https://discordapp.com/developers/docs/resources/webhook)
- Save [notify-discord.py](notify-discord.py) as **/data/etc/notify-discord.py** on your MotionEyeOS device
- Add the example command below in the MotionEyeOS UI under: **Settings > File Storage > Run A Command**

# Example Command:
python /data/etc/notify-discord.py -n "Kitchen Camera" -p %f --usetitle -q %q -t "%d/%m/%Y - %H:%M:%S" -v %v --hookid "someid" --hooktoken "sometoken"
