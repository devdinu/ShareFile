from __future__ import print_function
from datetime import datetime

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
