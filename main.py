import telebot
import datetime
from photosAPI.photos_grabber import GooglePhotoService

token = '<TOKEN>'
bot = telebot.TeleBot(token)
media = GooglePhotoService()


@bot.message_handler(commands=["start"])
def hello(msg):
    bot.send_message(msg.chat.id, "Hello! I am a bot created for send to this chat some interesting photos from "
                                  "family archive!")


@bot.message_handler(commands=["send_photo"])
def photo(msg):
    media.download_random_photo()
    img = open('downloads/photo.jpg', 'rb')
    bot.send_photo(msg.chat.id, img, caption='This my photo!')


def test_send_message():
    media.download_random_photo()
    img = open('downloads/photo.jpg', 'rb')

    text = 'Вот пришла кратная минута двум))'
    ret_msg = bot.send_message(25035106, text)
    bot.send_photo(25035106, img, caption='Держи фотку')
    assert ret_msg.message_id


if __name__ == '__main__':
    past_minute = -1

    while True:
        now = datetime.datetime.now()

        if now.minute % 2 == 0 and now.minute != past_minute:
            past_minute = now.minute
            test_send_message()