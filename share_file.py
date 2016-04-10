from __future__ import print_function
import sublime
import sublime_plugin
import requests
import json
from threading import Thread
from datetime import datetime

class ServiceApi:

    base_url = "http://localhost:8080/"

    def upload_content(self, name, content):
        response = requests.post(self.base_url + 'upload/'+ name , data = bytes(content, Contstants.encode_format))
        return response

    def search_files(self, pattern):
        result = requests.get(self.base_url + 'search/'+ pattern)
        files = json.loads(result.text).get('files', [])
        return files


class Contstants:
    default_prompt_share_msg = "Enter File Name to Share:"
    default_prompt_search_msg = "Enter File Name to Search:"
    re_enter_filename = "ReEnter File Name:"
    encode_format = "utf-8"


class ShareFileCommand(sublime_plugin.TextCommand):

    service = ServiceApi()

    def valid(self, name):
        return name is not ""

    def share_file(self, file_name):
        while not self.valid(file_name):
            file_name = self.get_name_to_share(Contstants.default_prompt_share_msg)
        file_content = self.get_file_content()
        self.service.upload_content(file_name, file_content)

    def get_timestamp(self):
        return datetime.now().strftime('%Y-%m-%d-%H:%M:%S')

    def get_name_to_share(self, prompt_message):
        timestamp = self.get_timestamp()
        return self.view.window().show_input_panel(
            prompt_message, "File-Name|" + timestamp, self.share_file, None, None)

    def get_file_content(self):
        region = sublime.Region(0, self.view.size())
        content = self.view.substr(region)
        return content

    def run(self, edit, **kwargs):
        Thread(target=self.get_name_to_share, args=(Contstants.default_prompt_share_msg,)).start()


class DownloadFileCommand(sublime_plugin.WindowCommand):

    service = ServiceApi()

    def download_selected_file(self, chosen_index):
        print("downloading file", self.found_files[chosen_index]['file_name'])

    def search_files(self, file_name):
        if not file_name:
            return
        self.found_files = self.service.search_files(file_name)
        print("Matchig files: ", len(self.found_files))
        if self.found_files:
            self.window.show_quick_panel([f.get('file_name') + " | " + f.get('created_at') for f in self.found_files], self.download_selected_file)

    def get_pattern_for_search(self, prompt_message):
        return self.window.show_input_panel(
            prompt_message, "File-Name", self.search_files, None, None)

    def run(self, **kwargs):
        Thread(target=self.get_pattern_for_search, args=(Contstants.default_prompt_search_msg,)).start()
