import sublime
import sublime_plugin

ST3 = int(sublime.version()) > 3000

if ST3:
    from .util import Util
    from .constants import Constants
    from .service_api import ServiceApi
else:
    from constants import Constants
    from util import Util
    from service_api import ServiceApi


class DownloadFileCommand(sublime_plugin.WindowCommand):
    def _formatted_text_option(self, name, time):
        return time + " : " + name

    def _download_and_show_options(self, file_name_object_id):
        file_content = ServiceApi.download_file_content(file_name_object_id)
        self.window.new_file().run_command("insert_snippet", {"contents": file_content})

    def download_selected_file(self, chosen_index):
        if chosen_index == -1:
            return None
        interested_file = self.found_files[chosen_index]
        print("downloading file", interested_file.get('file_name'))
        Util.run_in_background(self._download_and_show_options, interested_file.get('id'))

    def search_files(self):
        print("searching file for user:", self.user_key, " pattern:", self.file_pattern)
        self.found_files = ServiceApi.search_files(self.user_key, self.file_pattern)
        if self.found_files:
            files_list = [self._formatted_text_option(f.get('file_name'), f.get('created_at')) for f in
                          self.found_files]
            self.window.show_quick_panel(files_list, self.download_selected_file)

    def _get_file_pattern_to_search(self, file_pattern):
        self.file_pattern = file_pattern
        self.search_files()

    def _get_users_key_to_search(self, user_key):
        self.user_key = user_key
        self.window.show_input_panel(Constants.msg_for_file_pattern_input, Constants.default_file_pattern,
            self._get_file_pattern_to_search, None, None)

    def get_inputs_for_search(self, prompt_message):
        self.window.show_input_panel(
            prompt_message, Util.get_user_id(), self._get_users_key_to_search, None, None)

    def run(self, **kwargs):
        self.get_inputs_for_search(Constants.msg_for_user_key_input)
