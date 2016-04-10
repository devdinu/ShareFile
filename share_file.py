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
        if not pattern:
            return None
        result = requests.get(self.base_url + 'search/'+ pattern)
        files = json.loads(result.text).get('files', [])
        return files

    def download_file_content(self, file_object_id):
        return requests.get(self.base_url + 'files/'+ file_object_id).text


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

    def _formatted_text_option(self, max_name_length, name, time):
        return time + " : " + name

    def download_selected_file(self, chosen_index):
        interested_file = self.found_files[chosen_index]
        print("downloading file", interested_file.get('file_name'))
        file_content = self.service.download_file_content(interested_file.get('id'))
        SublimeHelper(self.window.window_id).open_new_tab_with(file_content)

    def search_files(self, file_name):
        self.found_files = self.service.search_files(file_name)
        print("Matching files: ", len(self.found_files))
        if self.found_files:
            max_name_length = max([len(f.get('file_name')) for f in self.found_files])
            files_list = [self._formatted_text_option(max_name_length, f.get('file_name'), f.get('created_at')) for f in self.found_files]
            self.window.show_quick_panel(files_list, self.download_selected_file)

    def get_pattern_for_search(self, prompt_message):
        return self.window.show_input_panel(
            prompt_message, "File-Name", self.search_files, None, None)

    def run(self, **kwargs):
        Thread(target=self.get_pattern_for_search, args=(Contstants.default_prompt_search_msg,)).start()



class SublimeHelper(sublime.Window):

    def open_new_tab_with(self, new_file_content):
        new_view = self.new_file(self.window_id)
        new_view.run_command('insert_text', {'content':new_file_content})


class InsertTextCommand(sublime_plugin.TextCommand):

    def run(self, edit, **kwargs):
        self.view.insert(edit, 0, kwargs.get('content'))
