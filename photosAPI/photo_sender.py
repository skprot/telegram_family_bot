import time
import sys

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
    def __init__(self, token):
        super().__init__(token=token)
        self.media = GooglePhotoService()
        self.time = datetime.utcnow()
        self.schedule = self.set_default_hours()
        self.past_hour = -1
        self.chat_id = -1

    @staticmethod
    def set_default_hours():
        return [1, 12]

    def set_new_hours(self, hours):
        utc_irk = -8

        for i in range(len(hours)):
            hours[i] += utc_irk

        self.schedule = hours

    def set_chat_id(self):
        try:
            self.chat_id = self.get_updates()[0].message.chat.id
        except IndexError:
            return False

    def send_scheduled_photo(self):
        if (self.time.hour in self.schedule) and (self.time.hour != self.past_hour):
            self.send_my_photo()
            self.past_hour = self.time.hour

    def send_my_photo(self):
        self.media.download_random_photo()
        img = open('downloads/photo.jpg', 'rb')
        self.send_photo(self.chat_id, img, caption='It is time for photos!')

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

            if self.chat_id == -1:
                self.set_chat_id()
            else:
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

            if self.chat_id == -1:
                self.set_chat_id()
            else:
                self.send_scheduled_photo()

        logger.info('Stopped polling.')
