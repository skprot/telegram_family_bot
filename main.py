import telebot

token = '836723555:AAEGQibwtvDFy4jNK3v9SaYyebIXxJowBj0'
bot = telebot.TeleBot(token)


@bot.message_handler(commands=["start"])
def hello(msg):
    bot.send_message(msg.chat.id, "Hello! I am a bot created for send to this chat some interesting photos from "
                                  "family archive!")


if __name__ == '__main__':
    bot.infinity_polling()

