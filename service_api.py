from __future__ import print_function
import json
import requests
import sublime

ST3 = int(sublime.version()) > 3000

if ST3:
    from .util import Util
    from .constants import Constants
else:
    from constants import Constants
    from util import Util


class ServiceApi:
    base_url = "http://sharefiles-liveasdev.rhcloud.com/"
    upload_content_url = base_url + "users/{user_id}/files/{file_name}"
    get_user_id_url = base_url + "users/create"
    search_files_url = base_url + "users/{user_id}/files/search?pattern={file_pattern}"
    delete_file_url = base_url + "users/{user_id}/files/{file_object_id}"

    @classmethod
    def _is_success(cls, response, status_code=Constants.SUCCESS_STATUS_CODE):
        return response.status_code == status_code

    @classmethod
    def _get_uid(cls):
        user_id = Util.get_user_id()
        if not user_id:
            print("welcome, creating id for you.")
            user_id = requests.get(cls.get_user_id_url).text
            Util.set_user_id(user_id)
        return user_id

    @classmethod
    def upload_content(cls, name, content):
        encoded_data = Util.encode_data(content)
        url = cls.upload_content_url.format(user_id=cls._get_uid(), file_name=name)
        response = requests.post(url, encoded_data)
        return cls._is_success(response, 201)

    @classmethod
    def search_files(cls, user_key, pattern):
        files = []
        if not pattern:
            return None
        result = requests.get(cls.search_files_url.format(user_id=user_key, file_pattern=pattern))
        if cls._is_success(result):
            files = json.loads(result.text).get('files', [])
        return files

    @classmethod
    def download_file_content(cls, file_object_id):
        return requests.get(cls.base_url + 'files/' + file_object_id).text

    @classmethod
    def delete_file(cls, file_object_id):
        requests.delete(cls.delete_file_url.format(user_id=Util.get_user_id(), file_object_id=file_object_id))
