from __future__ import print_function
import sublime

ST3 = int(sublime.version()) > 3000

if ST3:
    from .constants import Constants
else:
    from constants import Constants


class Util:
    """Utility class to Handle operations on ST2 and ST3 accordingly"""

    settings = sublime.load_settings(Constants.settings_file)

    @classmethod
    def set_user_id(cls, user_id):
        cls.settings.set("user_id", user_id)
        sublime.save_settings(Constants.settings_file)

    @classmethod
    def get_user_id(cls):
        user_id = cls.settings.get("user_id") if cls.settings else ""
        return user_id if user_id else ""

    @staticmethod
    def run_in_background(function_to_run, *function_args):
        if ST3:
            from threading import Thread
            Thread(target=function_to_run, args=function_args).start()
        else:
            from functools import partial
            sublime.set_timeout(partial(function_to_run, *function_args), Constants.timeout)

    @staticmethod
    def encode_data(data):
        if ST3:
            return bytes(data, Constants.encode_format)
        return data.encode(Constants.encode_format, 'replace')

    @staticmethod
    def formatted_text_option(name, time):
        return time + " : " + name

    @staticmethod
    def display_available_files(window, files, selection_callback):
        if files:
            formatted_file_names = [Util.formatted_text_option(f.get('file_name'), f.get('created_at')) for f in files]
            window.show_quick_panel(formatted_file_names, selection_callback)
