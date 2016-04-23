from __future__ import print_function
import sublime
import requests
import json

ST3 = int(sublime.version()) > 3000

if ST3:
    from .util import Util
    from .constants import Constants
else:
    from constants import Constants
    from util import Util


class ServiceApi:
    # base_url = "http://sharefiles-liveasdev.rhcloud.com/"
    base_url = "http://localhost:8080/"
    upload_content_url = base_url + "users/{user_id}/files/{file_name}"
    get_user_id_url = base_url + "users/create"

    @classmethod
    def _is_success(cls, response):
        return response.status_code == Constants.SUCCESS_STATUS_CODE

    @classmethod
    def _get_uid(cls):
        settings = sublime.load_settings(Constants.settings_file)
        user_id = settings.get("user_id")
        print("settings, ", user_id, dir(settings))
        if not user_id:
            print("welcome, creating id for you.")
            user_id = requests.get(cls.get_user_id_url).text
            settings.set("user_id", user_id)
            sublime.save_settings(Constants.settings_file)
        return user_id

    @classmethod
    def upload_content(cls, name, content):
        encoded_data = Util.encode_data(content)
        url = cls.upload_content_url.format(user_id=cls._get_uid(), file_name=name)
        response = requests.post(url, encoded_data)
        return cls._is_success(response)

    @classmethod
    def search_files(cls, pattern):
        files = []
        if not pattern:
            return None
        result = requests.get(cls.base_url + 'search/' + pattern)
        if cls._is_success(result):
            files = json.loads(result.text).get('files', [])
        return files

    @classmethod
    def download_file_content(cls, file_object_id):
        return requests.get(cls.base_url + 'files/' + file_object_id).text
