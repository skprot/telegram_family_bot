from photosAPI import photo_sender

token = '836723555:AAEGQibwtvDFy4jNK3v9SaYyebIXxJowBj0'
bot = photo_sender.PhotoSender(token)


def send_time_error(chat_id):
    bot.send_message(chat_id, f"Hello! Something wrong... Try to write the command in this way: "
                                  f"/set_hours 1 9 18 20")


@bot.message_handler(commands=["start"])
def hello(msg):
    bot.send_message(msg.chat.id, "Hello! I am a bot created for send to this chat some interesting photos from "
                                  "family archive!")


@bot.message_handler(commands=["send_photo"])
def photo(msg):
    bot.send_my_photo(msg.chat.id)


@bot.message_handler(commands=["get_insides"])
def info(msg):
    bot.send_message(msg.chat.id, f"time: {bot.time}, chat_id: {bot.user_schedule}, len: {len(bot.get_updates())} ")


@bot.message_handler(commands=["get_schedule"])
def info(msg):
    bot.send_message(msg.chat.id, f"Schedule: {bot.user_schedule[msg.chat.id]} UTC (Irkutsk +8)")


@bot.message_handler(commands=["set_hours"], content_types=['text'])
def set_hours(msg):
    hours = msg.text
    hours = hours.split(" ")
    hours.pop(0)

    if len(hours) == 0:
        send_time_error(msg.chat.id)
        return

    for i in range(len(hours)):
        try:
            hours[i] = int(hours[i])
        except ValueError:
            send_time_error(msg.chat.id)
            return

        if hours[i] > 23 or hours[i] < 0:
            send_time_error(msg.chat.id)
            return

    bot.send_message(msg.chat.id, f"Hello! You have changed the schedule "
                                  f"of this bot on {hours} hours by Irkutsk time")

    bot.set_new_user_schedule(msg.chat.id, hours)


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except:
            pass