# Inital version created by https://github.com/Bluscream. 
# Copied from here: https://github.com/ccrisan/motioneyeos/issues/1557#issuecomment-399685425

import pycurl, cStringIO, glob, os, json, pytz, datetime, time, argparse
class motionEyeDiscordWebHook(object):
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Discord Webhook URL", type=str)
    parser.add_argument("-n", "--name", help="Name of the camera", type=str, default="Camera")
    parser.add_argument("-p", "--path", help="Path of the camera output or direct path to image", type=str, default="/data/output/Camera1/")
    parser.add_argument("--debug", help="Prints debug infos to console", type=bool, default=False)
    parser.add_argument("-t", "--time", help="%%d/%%m/%%Y - %%H:%%M:%%S from motionEyeOS", type=str)
    parser.add_argument("-q", "--frame", help="%%q from motionEyeOS", type=int)
    parser.add_argument("-v", "--eventid", help="%%v from motionEyeOS", type=int)
    args = parser.parse_args()
    MESSAGE = " - Motion was detected on %s" % args.name

    def get_latest_file(self):
        if os.path.isfile(self.args.path) and not os.path.isdir(self.args.path):
            return self.args.path
        TODAYS_DATE = datetime.datetime.today().strftime('%d-%m-%Y')
        TODAYS_DATE_FOLDER = self.args.path + TODAYS_DATE + '/*.jpg'
        LIST_OF_FILES = glob.glob(TODAYS_DATE_FOLDER)
        try:
            return max(LIST_OF_FILES, key=os.path.getctime)
        except ValueError:
            return "" # '/data/output/noimage.jpg'

    def send_to_discord(self, FILENAME=""):
        buf = cStringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, self.args.url)
        c.setopt(c.WRITEFUNCTION, buf.write)
        c.setopt(c.HTTPHEADER, ["Content-Type: multipart/form-data"])
        c.setopt(c.USERAGENT, "MotionEyeOS")
        utc = pytz.timezone('UTC')
        now = utc.localize(datetime.datetime.utcnow())
        la = pytz.timezone(os.path.realpath('/data/etc/localtime').replace('/usr/share/zoneinfo/posix/',''))
        local_time = now.astimezone(la)
        CURRENT_TIME = local_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        if self.args.time:
            MESSAGE_TIME = self.args.time
        else:
            MESSAGE_TIME = local_time.strftime("%d/%m/%Y - %H:%M:%S")
        if self.args.frame: MESSAGE_TIME += " [Frame: %s]"%self.args.frame
        if os.path.isfile(FILENAME):
            c.setopt(c.HTTPPOST, [("payload_json", json.dumps({ "content": MESSAGE_TIME + self.MESSAGE,"embeds": [{"timestamp": CURRENT_TIME }] })), ("file", (c.FORM_FILE, FILENAME,))])
        else:
            c.setopt(c.HTTPPOST, [("payload_json", json.dumps({ "content": MESSAGE_TIME + self.MESSAGE }))])
        c.setopt(c.VERBOSE, self.args.debug)
        c.perform()
        c.close()
        f = buf.getvalue()
        buf.close()
        if self.args.debug: print(f)
        _path = self.args.path
        if os.path.isfile(_path) and not os.path.isdir(_path):
            os.remove(_path)
        thumbnail = "%s.thumb"%_path
        if os.path.isfile(thumbnail): os.remove(thumbnail)

if __name__ == '__main__':
    wh = motionEyeDiscordWebHook()
    wh.send_to_discord(wh.get_latest_file())
# python /data/notify-discord.py https://discordapp.com/api/webhooks/your-webhook-url-here -n "Kitchen" -p %f -q %q -t "%d/%m/%Y - %H:%M:%S" -v %v &
# python /data/discord.py https://discordapp.com/api/webhooks/your-webhook-url-here -n "Kitchen" -p /data/output/Camera2/2018-06-23/16-27-12m.mp4 -q 1 -t "11/11/1111 - 11:11:11" -v 1 &

# python /data/discord.py https://discordapp.com/api/webhooks/your-webhook-url-here -n "Networking Room" -p %f -q %q -t "%d/%m/%Y - %H:%M:%S" -v %v &
# python /data/discord.py https://discordapp.com/api/webhooks/your-webhook-url-here -n "Networking Room" -p /data/output/Camera1/ -q %q -t "%d/%m/%Y - %H:%M:%S" &
