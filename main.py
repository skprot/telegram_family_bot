import telebot
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
    text = 'CI Test Message'
    ret_msg = bot.send_message(25035106, text)
    assert ret_msg.message_id

if __name__ == '__main__':
    while True:
        #if TIME
        test_send_message()