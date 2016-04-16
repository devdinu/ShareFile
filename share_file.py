from __future__ import print_function
import sublime
import sublime_plugin
import requests
import json
from datetime import datetime

class Constants:

    default_prompt_share_msg = "Enter File Name to Share:"
    default_prompt_search_msg = "Enter File Name to Search:"
    re_enter_filename = "ReEnter File Name:"
    ST3 = int(sublime.version()) > 3000
    encode_format = "utf-8"
    timeout = 100
    SUCCESS_STATUS_CODE = 200


class Util:
    """Utility class to Handle operations on ST2 and ST3 accordingly"""

    @staticmethod
    def run_in_background(function_to_run, *function_args):
        if Constants.ST3:
            from threading import Thread
            Thread(target=function_to_run, args=function_args).start()
        else:
            from functools import partial
            sublime.set_timeout(partial(function_to_run, *function_args), Constants.timeout)

    @staticmethod
    def encode_data(data):
        if Constants.ST3:
            return bytes(data, Constants.encode_format)
        return data.encode(Constants.encode_format, 'replace')

class ServiceApi:
    base_url = "http://localhost:8080/" #"http://sharefiles-liveasdev.rhcloud.com/"

    @classmethod
    def _is_success(cls, response):
        return response.status_code==Constants.SUCCESS_STATUS_CODE

    @classmethod
    def upload_content(cls, name, content):
        encoded_data = Util.encode_data(content)
        response = requests.post(cls.base_url + 'upload/'+ name , encoded_data)
        return cls._is_success(response)

    @classmethod
    def search_files(cls, pattern):
        files = []
        if not pattern:
            return None
        result = requests.get(cls.base_url + 'search/'+ pattern)
        if cls._is_success(result):
            files = json.loads(result.text).get('files', [])
        return files

    @classmethod
    def download_file_content(cls, file_object_id):
        return requests.get(cls.base_url + 'files/'+ file_object_id).text



class ShareFileCommand(sublime_plugin.TextCommand):

    def _valid(self, name):
        return name is not ""

    def share_file(self, file_name):
        while not self._valid(file_name):
            file_name = self.get_name_to_share(Constants.default_prompt_share_msg)
        file_content = self.get_file_content()
        Util.run_in_background(ServiceApi.upload_content, file_name, file_content)

    def _get_timestamp(self):
        return datetime.now().strftime('%Y-%m-%d-%H:%M:%S')

    def get_name_to_share(self, prompt_message):
        timestamp = self._get_timestamp()
        return self.view.window().show_input_panel(
            prompt_message, "File-Name|" + timestamp, self.share_file, None, None)

    def get_file_content(self):
        entire_region = sublime.Region(0, self.view.size())
        return self.view.substr(entire_region)

    def run(self, edit, **kwargs):
        self.get_name_to_share(Constants.default_prompt_share_msg)


class DownloadFileCommand(sublime_plugin.WindowCommand):

    def _formatted_text_option(self, name, time):
        return time + " : " + name

    def _download_and_show_options(self, file_name_object_id):
        file_content = ServiceApi.download_file_content(file_name_object_id)
        self.window.new_file().run_command("insert_snippet", {"contents": file_content})

    def download_selected_file(self, chosen_index):
        if chosen_index==-1:
            return None
        interested_file = self.found_files[chosen_index]
        print("downloading file", interested_file.get('file_name'))
        Util.run_in_background(self._download_and_show_options, interested_file.get('id'))

    def search_files(self, file_name):
        self.found_files = ServiceApi.search_files(file_name)
        if self.found_files:
            files_list = [self._formatted_text_option(f.get('file_name'), f.get('created_at')) for f in self.found_files]
            self.window.show_quick_panel(files_list, self.download_selected_file)

    def get_pattern_for_search(self, prompt_message):
        return self.window.show_input_panel(
            prompt_message, "File-Name", self.search_files, None, None)

    def run(self, **kwargs):
        self.get_pattern_for_search(Constants.default_prompt_search_msg)
