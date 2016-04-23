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
    def _download_and_show_options(self, file_name_object_id):
        file_content = ServiceApi.download_file_content(file_name_object_id)
        self.window.new_file().run_command("insert_snippet", {"contents": file_content})

    def download_selected_file(self, chosen_index):
        if chosen_index == -1:
            return None
        interested_file = self.found_files[chosen_index]
        print("downloading file", interested_file.get('file_name'))
        Util.run_in_background(self._download_and_show_options, interested_file.get('id'))

    def _get_file_pattern_to_search(self, file_pattern):
        print("searching file for user:", self.user_key, " pattern:", file_pattern)
        self.found_files = ServiceApi.search_files(self.user_key, file_pattern)
        Util.display_available_files(self.window, self.found_files, self.download_selected_file)

    def _get_users_key_to_search(self, user_key):
        self.user_key = user_key
        self.window.show_input_panel(Constants.msg_for_file_pattern_input, Constants.default_all_files_pattern,
                                     self._get_file_pattern_to_search, None, None)

    def get_inputs_for_search(self):
        self.window.show_input_panel(
            Constants.msg_for_user_key_input, Util.get_user_id(), self._get_users_key_to_search, None, None)

    def run(self, **kwargs):
        self.get_inputs_for_search()
