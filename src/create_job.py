#!/usr/bin/env python
from gnip_historical.gnip_historical_cmd import *
import datetime
class CreatJob(GnipHistoricalCmd):
    def setOptions(self, parser):
        parser.add_option("-f", "--filename", dest="fileName", default=None,
	        help="File defining job (JSON)")
        parser.add_option("-t", "--title", dest="title", default=None,
	        help="Title of project, this title supercedes title in file if set.")

    def __call__(self):
        if self.options.fileName is None:
            print "Please provide a job description file. Use create_job.py -h for more information."
        else:    
            self.gnipHistorical.jobPars = JobParameters(self.options.title, jobFileName = self.options.fileName)
            print "#"*35
            print "CREATING JOB: (%s)"%self.gnipHistorical.jobPars.getTitle()
            print "PARAMETERS:"
            print str(self.gnipHistorical.jobPars)
            print "RESPONSE:"
            res = self.gnipHistorical.createJob()
            print str(res)
            if res.jobURL is not None:
                self.updateURLConfig(url = res.jobURL)

CreatJob()()
