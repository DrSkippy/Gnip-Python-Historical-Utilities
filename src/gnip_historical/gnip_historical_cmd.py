#!/usr/bin/env python
import ConfigParser
from optparse import OptionParser
from gnip_historical import *

DEFAULT_FILE_NAME='./.gnip'

class GnipHistoricalCmd(object):
    def __init__(self, jobPar=None):
        self.config = ConfigParser.ConfigParser()
        self.config.read(DEFAULT_FILE_NAME)
        un = self.config.get('creds', 'un')
        pwd = self.config.get('creds', 'pwd')
        endURL = self.config.get('endpoint', 'url')
        self.prevurl = self.config.get('tmp','prevUrl')
        parser = OptionParser()
        parser.add_option("-u", "--url", dest="url", default=None,
                    help="Job url.")
        parser.add_option("-l", "--prev-url", action="store_true", dest="prevUrl", default=False,
                    help="Use previous Job URL (only from this configuration file.).")
        parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                    help="Detailed output.")
        self.setOptions(parser)
        (self.options, self.optArgs) = parser.parse_args()
        self.updateURLConfig()
        self.gnipHistorical = GnipHistorical(un, pwd, endURL, jobPar)
        
    def setOptions(self, parser):
        # e.g. parser.add_option("-l", "--prev-url", action="store_true", dest="prevUrl", default=False,
        #            help="Use the prev Job URL.")
        pass

    def updateURLConfig(self, url = None):
        if self.options.prevUrl:
            self.userUrl = self.prevurl
        elif self.options.url is not None:
            self.userUrl = self.options.url
        elif url is not None:
            self.userUrl = url
        else:
            self.userUrl = None
        self.config.set('tmp','prevUrl',self.userUrl)
        with open(DEFAULT_FILE_NAME, 'wb') as self.configfile:
            self.config.write(self.configfile)

