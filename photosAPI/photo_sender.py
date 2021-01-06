import time
import sys
import os

import logging

logger = logging.getLogger('TeleBot')
formatter = logging.Formatter(
    '%(asctime)s (%(filename)s:%(lineno)d %(threadName)s) %(levelname)s - %(name)s: "%(message)s"'
)

console_output_handler = logging.StreamHandler(sys.stderr)
console_output_handler.setFormatter(formatter)
logger.addHandler(console_output_handler)

logger.setLevel(logging.ERROR)

from telebot import apihelper, util, TeleBot
from datetime import datetime
from photosAPI.photo_grabber import GooglePhotoService


class PhotoSender(TeleBot):
    def __init__(self, token, parse_mode=None, threaded=True, skip_pending=False, num_threads=2,
                 next_step_backend=None, reply_backend=None):
        super().__init__(token=token, parse_mode=parse_mode, threaded=threaded,
                         skip_pending=skip_pending, num_threads=num_threads,
                         next_step_backend=next_step_backend, reply_backend=reply_backend)
        self.media = GooglePhotoService()
        self.time = datetime.utcnow()
        self.schedule = self.set_default_hours()
        self.user_schedule = {}
        self.past_hour = {}
        self.chat_id = []
        self.ping_minute = -1

    @staticmethod
    def set_default_hours():
        return [1, 12]

    def ping(self):
        self.time = datetime.utcnow()
        if (self.time.minute % 15 == 0) and (self.time.minute != self.ping_minute):
            self.ping_minute = self.time.minute
            response = os.system("ping -c 1 google.com")
            if response == 0:
                print("ping OK")
            else:
                print("ping NOT OK")

    def set_default_user_schedule(self, chat_id):
        if chat_id not in self.user_schedule:
            self.user_schedule[chat_id] = self.set_default_hours()
            self.past_hour[chat_id] = -1
        else:
            self.user_schedule.update({chat_id: self.set_default_hours()})
            self.past_hour.update({chat_id: -1})

    def set_new_user_schedule(self, chat_id, schedule):
        utc_irk = -8

        for i in range(len(schedule)):
            if schedule[i] > 7:
                schedule[i] += utc_irk
            else:
                schedule[i] += utc_irk + 24

        if chat_id not in self.user_schedule:
            self.user_schedule[chat_id] = schedule
        else:
            self.user_schedule.update({chat_id: schedule})

    def set_chat_id(self):
        try:
            for i in range(len(self.get_updates())):
                if self.get_updates()[i].message.chat.id not in self.chat_id:
                    new_id = self.get_updates()[i].message.chat.id
                    self.chat_id.append(new_id)
                    self.set_default_user_schedule(new_id)
        except IndexError:
            return False

    def send_scheduled_photo(self):
        self.time = datetime.utcnow()
        for _id, schedule in self.user_schedule.items():
            if (self.time.hour in schedule) and (self.time.hour != self.past_hour[_id]):
                self.send_my_photo(_id)
                self.past_hour[_id] = self.time.hour

    def send_my_photo(self, chat_id):
        self.media.download_random_photo()
        img = open('downloads/photo.jpg', 'rb')
        self.send_photo(chat_id, img, caption='It is time for photos!')

    def polling(self, none_stop=False, interval=0, timeout=20):
        """
            Overrided method from parent class TeleBot
        """
        if self.threaded:
            self.__threaded_polling(none_stop, interval, timeout)
        else:
            self.__non_threaded_polling(none_stop, interval, timeout)

    def __threaded_polling(self, none_stop=False, interval=0, timeout=3):
        """
            Overrided method from parent class TeleBot
        """
        logger.info('Started polling.')
        self._TeleBot__stop_polling.clear()
        error_interval = 0.25

        polling_thread = util.WorkerThread(name="PollingThread")
        or_event = util.OrEvent(
            polling_thread.done_event,
            polling_thread.exception_event,
            self.worker_pool.exception_event
        )

        while not self._TeleBot__stop_polling.wait(interval):
            or_event.clear()
            try:
                polling_thread.put(self._TeleBot__retrieve_updates, timeout)

                or_event.wait()  # wait for polling thread finish, polling thread error or thread pool error

                polling_thread.raise_exceptions()
                self.worker_pool.raise_exceptions()

                error_interval = 0.25
            except apihelper.ApiException as e:
                logger.error(e)
                if not none_stop:
                    self._TeleBot__stop_polling.set()
                    logger.info("Exception occurred. Stopping.")
                else:
                    polling_thread.clear_exceptions()
                    self.worker_pool.clear_exceptions()
                    logger.info("Waiting for {0} seconds until retry".format(error_interval))
                    time.sleep(error_interval)
                    error_interval *= 2
            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt received.")
                self._TeleBot__stop_polling.set()
                break

            self.ping()
            self.set_chat_id()
            if len(self.user_schedule) > 0:
                self.send_scheduled_photo()

        polling_thread.stop()
        logger.info('Stopped polling.')

    def __non_threaded_polling(self, none_stop=False, interval=0, timeout=3):
        """
            Overrided method from parent class TeleBot
        """
        logger.info('Started polling.')
        self._TeleBot__stop_polling.clear()
        error_interval = 0.25

        while not self._TeleBot__stop_polling.wait(interval):
            self.send_scheduled_photo()
            try:
                self._TeleBot__retrieve_updates(timeout)
                error_interval = 0.25
            except apihelper.ApiException as e:
                logger.error(e)
                if not none_stop:
                    self._TeleBot__stop_polling.set()
                    logger.info("Exception occurred. Stopping.")
                else:
                    logger.info("Waiting for {0} seconds until retry".format(error_interval))
                    time.sleep(error_interval)
                    error_interval *= 2
            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt received.")
                self._TeleBot__stop_polling.set()
                break

            self.ping()
            if self.chat_id[0] == -1:
                self.set_chat_id()
            else:
                self.send_scheduled_photo()

        logger.info('Stopped polling.')
