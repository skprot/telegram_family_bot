import os
import pandas as pd
import requests
from photosAPI.client_creator import create_service
from random import randint


class GooglePhotoService:
    def __init__(self):
        self.API_NAME = 'photoslibrary'
        self.API_VERSION = 'v1'
        self.CLIENT_SECRET_FILE = 'client_secret_photobot.json'
        self.SCOPES = ['https://www.googleapis.com/auth/photoslibrary',
                       'https://www.googleapis.com/auth/photoslibrary.sharing']

        self.service = create_service(self.CLIENT_SECRET_FILE, self.API_NAME, self.API_VERSION, self.SCOPES)

    @staticmethod
    def _get_random_id(media_files_ids):
        random_id = randint(0, media_files_ids.shape[0])

        return random_id

    @staticmethod
    def _check_response():
        try:
            media_items_ids = pd.read_pickle("media_ids.pkl")
        except FileNotFoundError:
            return False

        media_id = media_items_ids.loc[0]
        url = media_id['baseUrl'] + '=d'
        request = requests.get(url)

        if request.status_code == 200:
            return True
        else:
            return False

    @staticmethod
    def _download(url, destination_folder, file_name):
        response = requests.get(url)

        if response.status_code == 200:
            new_file_name = 'photo.jpg'
            print('Downloading file {} as'.format(file_name), new_file_name)

            with open(os.path.join(destination_folder, new_file_name), 'wb') as f:
                f.write(response.content)
                f.close()
        else:
            response.raise_for_status()

    def _get_all_ids(self) -> None:
        print('Collecting media files list')
        media_files = self.service.mediaItems().list(pageSize=100).execute()
        lst_media = media_files.get('mediaItems')
        next_page_token = media_files.get('nextPageToken')

        while next_page_token:
            df_media_items = pd.DataFrame(lst_media)
            media_files = self.service.mediaItems().list(
                pageSize=100,
                pageToken=next_page_token
            ).execute()
            lst_media.extend(media_files.get('mediaItems'))
            next_page_token = media_files.get('nextPageToken')

        df_media_items.to_pickle("media_ids.pkl")

    def download_random_photo(self):
        if self._check_response():
            pass
        else:
            self._get_all_ids()

        media_items_ids = pd.read_pickle("media_ids.pkl")
        random_id_number = self._get_random_id(media_items_ids)
        media_id = media_items_ids.loc[random_id_number]

        download_url = media_id['baseUrl'] + '=d'
        download_folder = r'downloads'
        file_name = media_id['filename']

        try:
            os.mkdir(download_folder)
        except OSError:
            pass

        self._download(download_url, download_folder, file_name)
