import json
import os

import requests

from yandex_api import YaUploader


def get_profile_photos(owner_id, token):

    params = {
        'owner_id': owner_id,
        'access_token': token,
        'album_id': 'profile',
        'v': '5.81',
        'photo_sizes': '1',
        'extended': '1'
    }
    url = 'https://api.vk.com/method/photos.get'
    urls = []

    response = requests.get(
        url=url,
        params=params
    )
    if response.status_code == 200:
        json_output = response.json()
        print('json_output:', json_output)
        json_file_data = []

        for item in json_output['response']['items'][:5]:

            item_with_max_size = get_max_size(*item['sizes'])
            likes = item['likes']['count']
            date = item['date']

            print(json_file_data)
            print(item_with_max_size['url'])

            file_name = get_filename(
                url=item_with_max_size['url'],
                likes=likes,
                date=date,
                json_data=json_file_data
            )

            urls.append({
                'url': item_with_max_size['url'],
                'path': file_name
            })
            print('urls', urls)
            size = str(item_with_max_size['width']) + 'x' + str(item_with_max_size['height'])

            json_file_data.append(
                {
                    'file_name': file_name,
                    'size': size
                }
            )
        with open('photos.json', 'w') as file:
            file.write(json.dumps(json_file_data))
    else:
        print(response.status_code)
    return urls


def get_filename(url, likes, date, json_data):

    print('url:', url)
    print('likes:', likes)
    print('date:', date)
    print('json_data', json_data)

    response = requests.get(url=url)
    if response.status_code == 200:

        file_type = response.headers['Content-Type'].split('/')[1]

        file_name = str(likes) + '.' + file_type
        for item in json_data:

            if file_name == item['file_name']:
                file_name = str(likes) + str(date) + '.' + file_type
        print('file_name:', file_name)
        return file_name


def download_photo(url, likes, date):
    response = requests.get(url=url)
    if response.status_code == 200:
        directory = 'photos'
        file_type = response.headers['Content-Type'].split('/')[1]
        print(file_type)
        file_name = directory + '/' + str(likes) + '.' + file_type
        if os.path.exists(file_name):
            file_name = directory + '/' + str(likes) + str(date) + '.' + file_type
        with open(file_name, 'wb') as file:
            file.write(response.content)
        return file_name.split('/')[-1]


def get_max_size(*sizes):
    sizes_sorted = sorted(sizes, key=lambda item: item['height'])

    return sizes_sorted[-1]

if __name__ == '__main__':
    owner_id = input('Введите id пользователя VK: ')
    ya_token = input('Введите токен Яндекса: ')
    folder = input('Введите название папки для фото на Яндекс Диске: ')

    urls = get_profile_photos(
        owner_id=owner_id,
        token='958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
    )
    uploader = YaUploader(token=ya_token)
    upload_directory_created = uploader.check_directory_for_upload(folder)
    if upload_directory_created:
        for url in urls:

            upload_status, upload_error, upload_error_desc = uploader.upload_from_url(url=url['url'],
                                                                                      path=folder + '/' + url['path'])
            if upload_error:
                print('Произошла ошибка во время загрузки файла:')
                print('- Код ошибки:', str(upload_status))
                print('- Наименование ошибки:', str(upload_error))
                print('- Описание ошибки:', str(upload_error_desc))
            else:
                print('Файл отправлен для загрузки. Код ответа:', upload_status)
        if not len(urls):
            print('Не удалось получить список фото для загрузки.')
    else:
        print('Не удалось создать папку на яндекс диске!')
