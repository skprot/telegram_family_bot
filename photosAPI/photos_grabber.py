import os
import pandas as pd
import requests
from photosAPI.client_creator import create_service
from random import randint


class GooglePhotoService:
    def __init__(self):
        self.API_NAME = 'photoslibrary'
        self.API_VERSION = 'v1'
        self.CLIENT_SECRET_FILE = '../client_secret_photobot.json'
        self.SCOPES = ['https://www.googleapis.com/auth/photoslibrary',
                       'https://www.googleapis.com/auth/photoslibrary.sharing']

        self.service = create_service(self.CLIENT_SECRET_FILE, self.API_NAME, self.API_VERSION, self.SCOPES)

    @staticmethod
    def _get_random_id(media_files_ids):
        random_id = randint(0, media_files_ids.shape[0])

        return random_id

    def _download(self, url, destination_folder, file_name):
        response = requests.get(url)
        if response.status_code == 200:
            print('Downloading file {0}'.format(file_name))
            with open(os.path.join(destination_folder, 'photo.jpg'), 'wb') as f:
                f.write(response.content)
                f.close()
        else:
            self._get_all_ids()
            print('Download error with request response [{}]. Media files list were out of date!'.format(response.status_code))
            raise ValueError('Download error with request response [{}]. Media files list were out of date!')

    def _get_all_ids(self):
        print('Collecting media files list')
        media_files = self.service.mediaItems().list(pageSize=100).execute()
        lst_media = media_files.get('mediaItems')
        nextPageToken = media_files.get('nextPageToken')

        while nextPageToken:
            df_media_items = pd.DataFrame(lst_media)
            media_files = self.service.mediaItems().list(
                pageSize=100,
                pageToken=nextPageToken
            ).execute()

            lst_media.extend(media_files.get('mediaItems'))
            nextPageToken = media_files.get('nextPageToken')

        df_media_items.to_pickle("../media_ids.pkl")

    def download_random_photo(self):
        media_items_ids = pd.read_pickle("../media_ids.pkl")
        id = self._get_random_id(media_items_ids)
        media_id = media_items_ids.loc[id]
        download_url = media_id['baseUrl'] + '=d'
        download_folder = r'../downloads'
        file_name = media_id['filename']

        try:
            self._download(download_url, download_folder, file_name)
        except ValueError:
            print('Trying again!')
            self._download(download_url, download_folder, file_name)


#a = GooglePhotoService()
#a.download_random_photo()