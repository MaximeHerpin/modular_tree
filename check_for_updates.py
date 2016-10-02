import urllib.request
from html.parser import HTMLParser
import re

from bpy.types import Operator

VERSION = '"version"'


class SimpleParser(HTMLParser):
    result = []

    def handle_data(self, data):
        self.result.append(data)

    def get_results(self):
        return "".join(self.result)


class CheckForUpdates(Operator):
    """Make a tree"""
    bl_idname = "mod_tree.check_for_updates"
    bl_label = "Check for Updates"

    def execute(self, context):

        # get current __init__.py page from github
        with urllib.request.urlopen('https://github.com/MaximeHerpin/modular_tree/blob/master/__init__.py') as response:
            data = response.read()

        if response.reason == 'OK':

            html = data.decode('utf-8')

            parser = SimpleParser()
            parser.feed(html)
            page = parser.get_results()

            #                        "version ":    (n,   n )
            my_regex = re.compile(r'\"version\":\s*\(2,\s*7\)', re.DOTALL)
            # check if version number is on page
            if re.search(my_regex, page):
                self.report({'ERROR'}, "You have the latest official release.")
            else:
                self.report({'ERROR'}, "New update available!")

            return {'FINISHED'}

        else:
            self.report({'ERROR'}, "Could not connect: {} {}".format(response.status, response.reason))
            return {'CANCELLED'}
