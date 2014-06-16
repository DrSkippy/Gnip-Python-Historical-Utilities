#!/usr/bin/env python
import urllib2
import base64
import json
import sys
import datetime
from gnip_historical_job import *

#
class RequestWithMethod(urllib2.Request):
    # extend request to include explicit method
    def __init__(self, URL, method, data=None, headers={}):
        self._method = method
        urllib2.Request.__init__(self, URL, data, headers)

    def get_method(self):
        if self._method:
            return self._method
        else:
            return urllib2.Request.get_method(self) 
#
class DataSetResults(object):
    def __init__(self, resDict):
        #print resDict.keys()
        if "urlList" in resDict:
            self.dataURLs = resDict["urlList"]
        elif "url_list" in resDict:
            self.dataURLs = resDict["url_list"]
        else:
            self.dataURLs = []
        if "urlCount" in resDict:
            self.URLCount = int(resDict["urlCount"])
        elif "url_count" in resDict:
            self.URLCount = int(resDict["url_count"])
        else:
            self.URLCount = -1
        if "totalFileSizeBytes" in resDict:    
            self.fileSizeBytes = int(resDict["totalFileSizeBytes"])
        elif "total_file_size_bytes" in resDict:
            self.fileSizeBytes = int(resDict["total_file_size_bytes"])
        else:
            self.fileSizeBytes = -1
        if "susptectMinuteURL" in resDict:
            self.suspectMinuteURLs = resDict["suspectMinuteURL"]
        else:
            self.suspectMinuteURLs = []

    def write(self):
        with open("./data_files.txt", "wb") as f:
            for i in self.dataURLs:
                f.write("%s\n"%i)
        if self.suspectMinuteURLs <> []:
            with open("./suspect_files.txt", "wb") as f:
                for i in self.suspectMinuteURLs:
                    f.write("%s\n"%i)
    
    def __repr__(self):
        res = 'DATA SET:\n'
        res += ' No. of URLs ............. {0:,}\n'.format(self.URLCount)
        res += ' File size (bytes)........ {0:,}\n'.format(self.fileSizeBytes)
        if len(self.dataURLs) > 5:
            tmpList = self.dataURLs[:5] + ["..."]
        else:
            tmpList = self.dataURLs
        tmpStr = str('\n'.join(tmpList))
        res += ' Files (URLs) ............ %s\n'%(tmpStr)
        if len(self.suspectMinuteURLs) > 5:
            tmpList = self.suspectMinuteURLs[:5] + ["..."]
        else:
            tmpList = self.suspectMinuteURLs
        tmpStr = str('\n'.join(tmpList))
        if len(self.suspectMinuteURLs) > 0:
            res += ' Suspect (URLs) .......... %s\n'%(tmpStr)
        return res

#
#
#
class Result(object):
    def __init__(self, resDict, gnipHist):
        #print str(resDict)
        self.completedAt = datetime.datetime.strptime(DATE_RE.search(resDict["completedAt"]).group(0),DATEFMT)
        try:
            self.activityCount = int(resDict["activityCount"])
        except TypeError:
            self.activityCount = -1
        try:
            self.fileCount = int(resDict["fileCount"])
        except TypeError:
            self.fileCount = -1
        try:
            self.fileSize = float(resDict["fileSizeMb"])
        except TypeError:
            self.fileSize = -1
        #self.dataFileURL = repairStagingURLs(resDict["dataURL"])
        self.dataFileURL = resDict["dataURL"]
        self.gnipHist = gnipHist
        self.dataSetResult = None
        self.getDataSetResult()
        
    def getDataSetResult(self):
        if self.dataFileURL is not None:
            dataDict = self.gnipHist.getDataURLDict(self.dataFileURL)
            if dataDict is not None:
                self.dataSetResult = DataSetResults(dataDict)

    def write(self):
        if self.dataSetResult is not None:
            self.dataSetResult.write()

    def __repr__(self):
        res = 'RESULT:\n'
        res += ' Job completed at ........ %s\n'%(self.completedAt)
        res += ' No. of Activities ....... {0:,}\n'.format(self.activityCount)
        res += ' No. of Files ............ {0:,}\n'.format(self.fileCount)
        res += ' Files size (MB) ......... {0:,}\n'.format(self.fileSize)
        res += ' Data URL ................ %s\n'%(self.dataFileURL)
        if self.dataSetResult is not None:
            res += str(self.dataSetResult)
        return res

#
#
#
class Quote(object):
    def __init__(self, quoteDict):
        # print str(quoteDict)
        if "costDollars" in quoteDict:
            try:
                self.costDollars = float(quoteDict["costDollars"])
            except TypeError:
                self.costDollars = -1
        else:
            self.costDollars = -1
        self.estimatedActivityCount = int(quoteDict["estimatedActivityCount"])
        self.estimatedDurationHours = float(quoteDict["estimatedDurationHours"])
        self.estimatedFileSizeMb = float(quoteDict["estimatedFileSizeMb"])
        if "expiresAt" in quoteDict and quoteDict["expiresAt"] is not None:
            self.expiresAt = datetime.datetime.strptime(DATE_RE.search(quoteDict["expiresAt"]).group(0), DATEFMT)
        else:
            self.expiresAt = "N/A"

    def __repr__(self):
        res = 'QUOTE:\n'
        res += ' Est. Cost ............... $ %.2f\n'%(self.costDollars)
        res += ' Est. No. of Activities .. {0:,}\n'.format(self.estimatedActivityCount)
        res += ' Est. Hours to Complete .. %.1f\n'%(self.estimatedDurationHours)
        res += ' Est. # filesize (MB)..... {0:,}\n'.format(self.estimatedFileSizeMb)
        res += ' Expires at .............. %s\n'%(self.expiresAt)
        return res

#
#
#
class Status(object):
    """This and jobParameters have the same base class?"""
    def __init__(self, statusDict, gnipHist=None):
        #print str(statusDict)
        if statusDict is None:
            self.status = 'Error retrieving Job status'
            self.statusMessage = 'Please verify your connection parameters and network connection'
            self.title = "N/A"
            self.jobURL = None
        else:
            #
            self.title = statusDict["title"]
            self.publisher = statusDict["publisher"]
            self.streamType = statusDict["streamType"]
            self.fromDate = datetime.datetime.strptime(statusDict["fromDate"], SHORT_DATEFMT)
            self.toDate = datetime.datetime.strptime(statusDict["toDate"], SHORT_DATEFMT)
            # self.jobURL = repairStagingURLs(statusDict["jobURL"])
            self.jobURL = statusDict["jobURL"]
            # Possible job progress
            self.requestedBy = self.set("requestedBy", statusDict)
            self.account = self.set("account", statusDict)
            self.format = self.set("format", statusDict)
            self.status  = self.set("status", statusDict)
            self.statusMessage  = self.set("statusMessage", statusDict)
            if "percentComplete" in statusDict:
                self.percentComplete = float(self.set("percentComplete",statusDict))
            else:
                self.percentComplete = 0.0
            if "requestedAt" in statusDict:
                self.requestedAt = datetime.datetime.strptime(DATE_RE.search(statusDict["requestedAt"]).group(0), DATEFMT)
            else:
                self.requestedAt = None
            if "acceptedAt" in statusDict: 
                self.acceptedAt = datetime.datetime.strptime(DATE_RE.search(statusDict["acceptedAt"]).group(0),DATEFMT)
                self.acceptedBy = statusDict["acceptedBy"]
            else:
                self.acceptedAt = None
                self.acceptedBy = None
            if "quote" in statusDict:
                self.quote = Quote(statusDict["quote"])
            else:
                self.quote = None
            if "results" in statusDict and gnipHist is not None:
                self.result = Result(statusDict["results"], gnipHist)
            else:
                self.result = None

    def set(self, f, d, n=False):
        if f in d:
            return d[f]
        else:
            if n:
                return -1
            else:
                return None

    def __repr__(self):
        res = '*'*(8+len(self.title)) + '\n'
        res += '*** %s ***\n'%self.title
        res += '*'*(8+len(self.title)) + '\n\n'
        if self.jobURL is None:
            return res
        if self.acceptedAt is not None:
            res += 'Job accepted date ........ %s\n'%self.acceptedAt
        res += 'From date ................ %s\n'%self.fromDate
        res += 'To date .................. %s\n'%self.toDate
        res += 'Request date ............. %s\n'%self.requestedAt
        res += 'Status ................... %s\n'%self.status
        res += 'Status message ........... %s\n'%self.statusMessage
        res += 'Percent complete ......... %2.2f\n'%self.percentComplete
        if self.quote is not None:
            res += str(self.quote)
        if self.result is not None:
            res += str(self.result)
        return res

#
#
#
class GnipHistorical(object):
    def __init__(self, UN, PWD, baseUrl, jParsObj = None):
        self.base64string = base64.encodestring('%s:%s' % (UN, PWD)).replace('\n', '')
        self.baseUrl = baseUrl
        self.jobPars = jParsObj
        self.status = None  # status object created when job status is retrieved

    def acceptJob(self, jobURL):
        res = self.PUT(jobURL, json.dumps({"status":"accept"}))
        if res is not None:
            return res["status"]
        else:
            return "Already accepted or rejected that job?" 

    def rejectJob(self, jobURL):
        res = self.PUT(jobURL, json.dumps({"status":"reject"}))
        if res is not None:
            return res["status"]
        else:
            return "Already accepted or rejected that job?" 

    def PUT(self, URL, msg):
        return self.POST_PUT(URL, msg, 'PUT')

    def createJob(self):
        res = self.POST(self.baseUrl + "jobs.json", str(self.jobPars))
        return Status(res)

    def POST(self, URL, msg):
        return self.POST_PUT(URL, msg, 'POST')

    def POST_PUT(self, URL, msg, method):
        try:
            req = RequestWithMethod(URL, method, data=msg)
            req.add_header('Content-type', 'application/json')
            req.add_header("Authorization", "Basic %s" % self.base64string)
            response = urllib2.urlopen(req)
            res = response.read()
        except urllib2.URLError, reason:
            sys.stderr.write("Check parameters, URL and authentication and validate job JSON. (%s)\n\n\n"%reason)
            return None
        try:
            return json.loads(res)
        except ValueError:
            return {"status": "Status Error: Server failed to return valid JSON object"}

    def listJobs(self):
        job = self.GET(self.baseUrl + "jobs.json")
        if job is not None and "jobs" in job:
            for x in job["jobs"]:
                yield Status(x)

    def GET(self, jobURL):
        try:    
            req = RequestWithMethod(jobURL, 'GET')
            req.add_header('Content-type', 'application/json')
            req.add_header("Authorization", "Basic %s" % self.base64string)
            response = urllib2.urlopen(req)
            res = response.read()
        except urllib2.URLError, reason:
            sys.stderr.write("Check parameters, URL and authentication. (%s)\n\n\n"%reason)
            return None
        try:
            return json.loads(res)
        except ValueError:
            return {"status": "Status Error: Server failed to return valid JSON object"}
        
    def getDataURLDict(self, URL):
        try:
            res = self.GET(URL)
        except ValueError:
            sys.stderr.write("No job matching the URL. (%s)\n"%URL)
            res = None 
        except AttributeError:
            sys.stderr.write("Url failed to return results. (%s)\n"%URL)
            res = None
        except TypeError:
            sys.stderr.write("Url failed to return results. (%s)\n"%URL)
            res = None
        return res

    def getJobStatusDict(self, jobURL = None):
        if jobURL is None:
            try:
                jobURL = self.status.jobURL
            except:
                sys.stderr.write("No job specified.\n")
                return None
        return self.GET(jobURL)

    def getJobStatus(self, jobURL = None):
        self.jobStatus(jobURL)
        return self.status

    def jobStatus(self, jobURL = None):
        # call jobStatus to get latest from server
        res = self.getJobStatusDict(jobURL)
        self.status = Status(res, self)
        return ' - '.join([self.status.status, self.status.statusMessage]) 

    def quote(self, jobURL = None):
        # uses existing record if possible
        if self.status is None:
            self.jobStatus(jobURL)
        if "quote" in self.status:
            return self.status.quote
        else:
            sys.stderr.write("No quote available.\n")
            return None

    def results(self, jobURL = None):
        # uses existing record if possible
        if self.status is None:
            self.jobStatus(jobURL)
        if self.status.result is not None:
            return self.status.result
        else:
            sys.stderr.write("No results available.\n")
            return None

#
#
#
if __name__ == '__main__':
    # Run some simple demos/tests
    ####################################
    # Working with job parameters
    # Example 1
    from pprint import pprint
    jp = JobParameters("BieberJob1")
    jp.setFromDate("2012-01-01T00:00:00")
    jp.setToDate("2012-01-01T00:01:00")
    tmp = jp.getToDate()
    jp.setToDate("201201010001") # same as above
    print jp.getToDate(), "=", tmp
    jp.setUser("DrSkippy27")
    jp.addRule("bieber", "bestRuleEver")
    # job json as string
    print jp
    # job json as dict
    pprint(jp.job)
    print "Job duration = ",jp.duration().seconds
    print
    # Example 2
    # save job description in file
    jp.writeToFile("./bieber_job1.json")
    # Example 3
    # read job description from file
    jp1 = JobParameters("BieberJob2", jobFileName = "./FileMissing.JSON") # this file doesn't exist
    jp1 = JobParameters("BieberJob2", jobFileName = "./bieber_job1.json")
    print jp1
    print
    # mess it up
    jp1.setFromDate("2012-01-01T00:02:00")
    try:
        print jp1 # error
    except ValueError, e:
        print e
    print
    # Example 4
    # working with rules
    jp3 = JobParameters("BieberJob2", jobFileName = "./bieber_job1.json")
    jp3.setRules([{"value": "no bieber"}])
    print jp3
    jp3.addRule("belieber")
    print jp3
    jp3.setRules('[{value":"one"}]') # error this is missing a quote
    jp3.setRules('[{"value":"one"}]')
    print jp3
    ####################################
    # Historical 1 - Change if you want to hit the server
    # r = GnipHistorical("user", "password", "https://historical.gnip.com/accounts/<yours>", jp)
    # Creates a job
    # print r.createJob()
    try:
        r.acceptJob("not a URL") # error
    except ValueError,e:
        print e
    # r.rejectJob("not a URL") # error
    # r.jobStatus("not a URL") # error
    # r.jobs() # get a list of jobs from the gnip server
