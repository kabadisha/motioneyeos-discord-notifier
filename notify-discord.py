# Inital version created by https://github.com/Bluscream and https://github.com/IAmOrion
# Originally copied from here: https://github.com/ccrisan/motioneyeos/issues/1557#issuecomment-399692426 and then modified slightly

# Installation:
# Save this file as /data/etc/notify-discord.py on your MotionEyeOS device
# Add the example command below in the MotionEyeOS UI under: Settings > File Storage > Run A Command

# Example Command:
# python /data/etc/notify-discord.py -n "Kitchen Camera" -p %f --usetitle -q %q -t "%d/%m/%Y - %H:%M:%S" -v %v --hookid "someid" --hooktoken "sometoken"

import pycurl, cStringIO, glob, os, json, pytz, datetime, time, argparse
from argparse import RawDescriptionHelpFormatter

class motionEyeDiscordWebHook(object):
    parser = argparse.ArgumentParser(description="Discord Webhook Script for MotionEye.\nYou can use this script as a Motion Event Notification",epilog="Written by James Tanner aka IAmOrion.\nhttps://github.com/IAmOrion\n ", formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("--hookid", help="Discord webhook id", type=str)
    parser.add_argument("--hooktoken", help="Discord webhook token", type=str)
    parser.add_argument("-n", "--name", help="Camera name", type=str, default="Camera")
    parser.add_argument("-p", "--path", help="Camera folder path", type=str, default="/data/output/Camera1/")
    parser.add_argument("--usetitle", help="Adds a message title.  Customise with --title 'Your Title' ", action='store_true')
    parser.add_argument("--title", help="Message Title", type=str, default = "__**Motion Detected!**__\n\n")
    parser.add_argument("-m", "--mention", help="Mention User(s)", type=str)
    parser.add_argument("-f", "--folder", help="Still Image -> Image File Name - eg if Image File Name is set to %%d-%%m-%%Y/%%H-%%M-%%S we want the folder, in this case it would be %%d-%%m-%%Y", type=str, default="%d-%m-%Y")
    parser.add_argument("-l", "--lastsnap", help="Uses MotionEye's lastsnap.jpg alias - only valid when using LOCAL Storage.  Won't work with Network Shared Storage", action='store_true')
    parser.add_argument("-t", "--time", help="%%d/%%m/%%Y - %%H:%%M:%%S from motionEyeOS", type=str)
    parser.add_argument("--datetimeformat", help="For example: %%d/%%m/%%Y - %%H:%%M:%%S", type=str, default="%d/%m/%Y - %H:%M:%S")
    parser.add_argument("-q", "--frame", help="%%q option from motionEyeOS (Frame number)", type=int)
    parser.add_argument("-v", "--eventnumber", help="%%v from motionEyeOS", type=int)
    parser.add_argument("--noimage", help="If no picture found, sends a 'noimage' placeholder instead of sending no image at all. Image used must exist at: /data/output/noimage.jpg", action='store_true')
    parser.add_argument("--delete", help="Will delete file(s) after sending", action='store_true')
    parser.add_argument("--debug", help="Prints debug information to console", action='store_true')
    args = parser.parse_args(); MESSAGE = ""

    if args.debug:
        print("Notifying Discord")

    if args.usetitle:
        MESSAGE += "%s" % args.title

    if args.mention:
        MESSAGE += "%s " % args.mention

    def get_latest_file(self):
        if os.path.isfile(self.args.path) and not os.path.isdir(self.args.path):
            return self.args.path

        TODAYS_DATE = datetime.datetime.today().strftime(self.args.folder)
        TODAYS_DATE_FOLDER = self.args.path + TODAYS_DATE + '/*.jpg'
        LIST_OF_FILES = glob.glob(TODAYS_DATE_FOLDER)
        try:
            return max(LIST_OF_FILES, key=os.path.getctime)
        except ValueError:
            if self.args.lastsnap and os.path.isfile(self.args.path + "lastsnap.jpg") and not os.path.isdir(self.args.path + "lastsnap.jpg"):
                    return self.args.path + "lastsnap.jpg"
            else:
                if self.args.noimage:
                    return "/data/output/noimage.jpg"
                else:
                    return ""

    def send_to_discord(self, FILENAME=""):
        buf = cStringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, "https://discordapp.com/api/webhooks/" + self.args.hookid + "/" + self.args.hooktoken)
        c.setopt(c.WRITEFUNCTION, buf.write)
        c.setopt(c.HTTPHEADER, ["Content-Type: multipart/form-data"])
        c.setopt(c.USERAGENT, "MotionEyeOS")
        utc = pytz.timezone('UTC')
        now = utc.localize(datetime.datetime.utcnow())
        la = pytz.timezone(os.path.realpath('/data/etc/localtime').replace('/usr/share/zoneinfo/posix/',''))
        local_time = now.astimezone(la)

        UTC_TIMESTAMP = local_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        MESSAGE_TIME = local_time.strftime(self.args.datetimeformat)

        if self.args.time: MESSAGE_TIME += " (MEOS Time: %s)" % self.args.time
        if self.args.frame: MESSAGE_TIME += " [Frame: %s]" % self.args.frame

        self.MESSAGE += MESSAGE_TIME + " | Motion was detected on %s" % self.args.name

        if os.path.isfile(FILENAME):
            c.setopt(c.HTTPPOST, [("payload_json", json.dumps({ "content": self.MESSAGE })), ("file", (c.FORM_FILE, FILENAME,))])
        else:
            c.setopt(c.HTTPPOST, [("payload_json", json.dumps({ "content": self.MESSAGE }))])

        c.setopt(c.VERBOSE, self.args.debug)
        c.perform()
        c.close()
        f = buf.getvalue()
        buf.close()

        if self.args.delete:
            _path = self.args.path

            if os.path.isfile(_path) and not os.path.isdir(_path):
                os.remove(_path)
                thumbnail = "%s.thumb" % _path

                if os.path.isfile(thumbnail): os.remove(thumbnail)

        if self.args.debug: print(f)

if __name__ == '__main__':
    wh = motionEyeDiscordWebHook()
    wh.send_to_discord(wh.get_latest_file())
