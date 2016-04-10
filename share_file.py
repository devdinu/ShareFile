from __future__ import print_function
import sublime
import sublime_plugin
import requests
from threading import Thread
from datetime import datetime

class Contstants:
    default_prompt_message = "Enter FileName to Share"
    re_enter_filename = "ReEnter File Name:"

class ShareFileCommand(sublime_plugin.TextCommand):

    # def __init__(self, view):
    service = ServiceApi()

    def valid(self, name):
        return name is not ""

    def share_file(self, file_name):
        while not self.valid(file_name):
            file_name = self.get_name_to_share(Contstants.default_prompt_message)
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
        Thread(target=self.get_name_to_share, args=(Contstants.default_prompt_message,)).start()


class ServiceApi:

    base_url = "http://localhost:8080/"

    def upload_content(self, name, content):
        response = requests.post(self.base_url + 'upload/'+ name , data = bytes(content,Config.encode_format))
        return response
