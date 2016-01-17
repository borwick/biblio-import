#!python
"""
This code reads a YAML file for configuration information and then
goes about logging into BiblioCommons, searching for stuff, and adding
it to your BiblioCommons "read later" list.

Timeouts of 2 seconds are built-in before every request.
"""
import logging                  # Needed for grab logs
import time                     # Needed for sleep
import urllib                   # Needed for search term quoting

from weblib.error import DataNotFound # Needed for when grab does not
                                      # find a regex match in the
                                      # search results
from grab import Grab                 # Needed for request mechanization
import yaml                           # Needed for configuration

# TODO make the config filename a command-line option.
CONFIG = yaml.load(open("config.yml"))

# Check to make sure all required config options are set
for config_arg in ('login_url', 'search_placeholder_url', 'successful_login_url',
                   'username', 'pin', 'search_file'):
    if config_arg not in CONFIG:
        # TODO make this a better exception
        raise Exception("Configuration argument '{}' not set in config file".format(config_arg))

# Show all logs
logging.basicConfig(level=logging.DEBUG)


class BiblioCommonsLoginException(Exception):
    """
    This exception is raised when `successful_login_url` is not returned by the login.

    This is the best way I know to tell whether the login worked, as
    200 is raised even for an invalid login.
    """
    pass


class BiblioCommonsDuplicateException(Exception):
    """
    This exception is raised when more than one search result can be
    added to your "read later" list.
    """
    pass


class BiblioCommons(object):
    LOGIN_URL = CONFIG['login_url']
    SUCCESSFUL_LOGIN_URL = CONFIG['successful_login_url']
    SEARCH_PLACEHOLDER_URL = CONFIG['search_placeholder_url']

    def __init__(self, username, pin):
        """
        Log in to BiblioCommons.
        """
        self.grab = Grab()
        time.sleep(2)
        self.grab.go(self.LOGIN_URL)
        self.grab.set_input('name', username)
        self.grab.set_input('user_pin', pin)
        resp = self.grab.submit()
        if resp.url != self.SUCCESSFUL_LOGIN_URL:
            raise BiblioCommonsLoginException("Bad username/PIN?")

    def search_and_add(self, search_string):
        """
        Escapes `search_string` and uses .format() to send it to the
        configured `search_placeholder_url`.

        Looks for the string `/collection/add/my/library` in the
        response. If it sees more than one it raises
        BiblioCommonsDuplicateException. If it sees one, it goes to
        that URL. If it sees zero matches, it does nothing.
        """
        escaped_search_string =urllib.quote(search_string)
        search_url = self.SEARCH_PLACEHOLDER_URL.format(escaped_search_string)
        time.sleep(2)
        resp = self.grab.go(search_url)

        try:
            add_links = resp.rex_search('(/collection/add/my/library?[^"]+)').groups()
            if len(add_links) != 1:
                raise BiblioCommonsDuplicateException("Found {} links for search".format(len(add_links)))
            time.sleep(2)
            self.grab.go(add_links[0])
        except DataNotFound:
            pass


if __name__ == '__main__':
    # Read in the search file:
    with open(CONFIG['search_file']) as st_fh:
        # Log in:
        bc = BiblioCommons(username=CONFIG['username'],
                                  pin=CONFIG['pin'])
        # For each line:
        for line in st_fh.xreadlines():
            # Remove spaces. Is it then blank?
            line = line.strip()
            if line == '':
                continue
            # If not blank, search for the line and add it to your
            # "read later" list.
            bc.search_and_add(line)
