from __future__ import print_function
import sublime

ST3 = int(sublime.version()) > 3000

if ST3:
    from .constants import Constants
else:
    from constants import Constants

class Util:
    """Utility class to Handle operations on ST2 and ST3 accordingly"""

    @staticmethod
    def run_in_background(function_to_run, *function_args):
        if ST3:
            from threading import Thread
            Thread(target=function_to_run, args=function_args).start()
        else:
            from functools import partial
            sublime.set_async_timeout(partial(function_to_run, *function_args), Constants.timeout)

    @staticmethod
    def encode_data(data):
        if ST3:
            return bytes(data, Constants.encode_format)
        return data.encode(Constants.encode_format, 'replace')

