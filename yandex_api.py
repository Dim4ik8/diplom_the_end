import requests
from urllib.parse import urlencode


class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def check_directory_for_upload(self, folder):

        url_for_create = 'https://cloud-api.yandex.net:443/v1/disk/resources'
        created = False
        error = None
        description = None
        check_directory_request = requests.put(
            url=url_for_create,
            headers={'Authorization': self.token},
            params={'path': folder}
        )

        if check_directory_request.status_code == 409:
            created = True
            print('Директория уже существует!')
        elif check_directory_request.status_code == 201:
            created = True
            print('Директория создана!')
        else:
            print('При создании директории произошла ошибка!')
            error = check_directory_request.json()['error']
            description = check_directory_request.json()['description']
        return created, error, description

    def upload(self, file_path: str):

        url_for_prepare = 'https://cloud-api.yandex.net:443/v1/disk/resources/upload'

        upload_url = ''

        file_name = file_path.split('/')[-1]
        request_params = {'path': '/upload/' + file_name}

        params_encoded = urlencode(request_params)

        get_upload_url_request = requests.get(
            url=url_for_prepare + '?' + params_encoded,
            headers={'Authorization': self.token}
        )
        print("Код ответа первого запроса:" + str(get_upload_url_request.status_code))
        if get_upload_url_request.status_code == 200:
            response_data = get_upload_url_request.json()
            upload_url = response_data['href']
            print(upload_url)
        elif get_upload_url_request.status_code == 401:
            print('401 Вы не авторизованы')

        if upload_url != '':
            file_upload_request = requests.put(
                url=upload_url,
                data=open(file_path, 'rb'),
                headers={'Authorization': self.token}
            )
            if file_upload_request.status_code == 201:
                print('Файл успешно загружен.')
            elif file_upload_request.status_code == 507:
                print('Недостаточно места на диске!')

    def upload_from_url(self, url: str, path: str):

        yandex_api_url = 'https://cloud-api.yandex.net:443/v1/disk/resources/upload'

        request_params = {
            'path': path,
            'url': url
        }
        params_encoded = urlencode(request_params)
        file_upload_request = requests.post(
            url=yandex_api_url + '?' + params_encoded,
            headers={'Authorization': self.token}
        )
        status = file_upload_request.status_code
        error = None
        description = None
        if status == 202:

            async_status_request = requests.get(
                url=file_upload_request.json()['href'],
                headers={'Authorization': self.token}
            )
            if async_status_request.status_code == 200:
                print('Статус операции загрузки файла: "{}"'.format(async_status_request.json()['status']))
            else:
                code = async_status_request.status_code
                error = async_status_request.json()['error']
                description = async_status_request.json()['description']
                print('Ошибка при выполнении загрузки файла.\n'
                      '  Код ответа: {}.\n'
                      '  Тип ошибки: {}\n'
                      '  Описание ошибки: {}\n'.format(code, error, description))

        elif status == 400:
            print('Некорректные данные.')
            """
                {
                  "message": "string",
                  "description": "string",
                  "error": "string"
                }
            """
        elif status == 401:
            print('Не авторизован.')
        elif status == 403:
            print('API недоступно. Ваши файлы занимают больше места, чем у вас есть.'
                  ' Удалите лишнее или увеличьте объём Диска.')
        elif status == 406:
            print('Ресурс не может быть представлен в запрошенном формате.')
        elif status == 409:
            print('Указанного пути "{path}" не существует.')
        elif status == 429:
            print('Слишком много запросов.')
        elif status == 503:
            print('Сервис временно недоступен.')
        elif status == 507:
            print('Недостаточно свободного места.')

        if status != 202:

            error = file_upload_request.json()['error']
            description = file_upload_request.json()['description']

        return status, error, description
