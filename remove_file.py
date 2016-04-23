from __future__ import print_function
import sublime
import sublime_plugin

if int(sublime.version()) > 3000:
    from .service_api import ServiceApi
    from .util import Util
    from .constants import Constants
else:
    from service_api import ServiceApi
    from util import Util
    from constants import Constants


class RemoveFileCommand(sublime_plugin.WindowCommand):
    def delete_file(self, chosen_index):
        if chosen_index == -1:
            return None
        file_to_delete = self.user_files[chosen_index]
        print("deleting file: ", file_to_delete)
        Util.run_in_background(ServiceApi.delete_file, file_to_delete.get('id'))

    def run(self, **kwargs):
        self.user_files = ServiceApi.search_files(Util.get_user_id(), Constants.default_all_files_pattern)
        Util.display_available_files(self.window, self.user_files, self.delete_file)
