#!/usr/bin/env python
from gnip_historical.gnip_historical_cmd import *
class RejectJob(GnipHistoricalCmd):
    def __call__(self):
        if self.userUrl is None:
            print "Please provide a job URL. Use reject_job.py -h for more information."
        else:
            print "RESULT:"
            print str(self.gnipHistorical.rejectJob(self.userUrl))
RejectJob()()
