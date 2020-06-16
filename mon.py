import time
import telepot
from telepot.loop import MessageLoop
import secret
import logging
import subprocess
import inquirer

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Wnck", "3.0")
from gi.repository import Gtk, Wnck

logging.basicConfig(filename="log.txt", level=logging.DEBUG)
rootLogger = logging.getLogger()
consoleHandler = logging.StreamHandler()
# consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)


class MyBot(telepot.Bot):
    def __init__(self, telegram_whitelist_chat_id, window_name: str, *args, **kwargs):
        super(MyBot, self).__init__(*args, **kwargs)
        self.answerer = telepot.helper.Answerer(self)
        self._message_with_inline_keyboard = None
        self.window_name = window_name
        self.telegram_whitelist_chat_id = telegram_whitelist_chat_id
        self.refresh_x_id()

    def refresh_x_id(self):
        screen = Wnck.Screen.get_default()
        screen.force_update()

        xid = None
        for window in screen.get_windows():
            if window.get_name() == answers["window_name"]:
                xid = window.get_xid()

        if not xid:
            for window in screen.get_windows():
                if window.get_name().startswith(answers["window_name"]):
                    xid = window.get_xid()

        if not xid:
            raise RuntimeError("no window found with name: " + answers["window_name"])
        self.xid = xid

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        logging.debug(str(content_type) + ' ' + str(chat_type) + " - " + str(chat_id))
        if chat_id in self.telegram_whitelist_chat_id:
            if content_type == 'text':
                if msg['text'] == '/capture':
                    bot.sendChatAction(chat_id, 'typing')
                    bot.sendMessage(chat_id, "Capturing image")
                    try:
                        self.capture_img()
                    except:
                        self.refresh_x_id()
                        self.capture_img()
                    bot.sendPhoto(chat_id, photo=open('img\\screenshot.png', 'rb'))

        else:
            bot.sendMessage(chat_id, "Not admin")

    def capture_img(self):
        subprocess.check_call(['convert', 'x:' + str(self.xid), 'img\\screenshot.png'], shell=False)


Gtk.init([])
screen = Wnck.Screen.get_default()
screen.force_update()
names = []
for window in screen.get_windows():
    names.append(window.get_name())

questions = [
    inquirer.List('window_name',
                  message="What Windows should be captured?\n",
                  choices=names),
]
try:
    answers = inquirer.prompt(questions)
except:
    # for running in IDE
    answers = dict(window_name="Telegram")

logging.info("starting...")
bot = MyBot(secret.telegram_whitelist_chat_id, answers['window_name'], secret.telegram_token)
MessageLoop(bot).run_as_thread()
logging.info("listening...")

while 1:
    time.sleep(10)
