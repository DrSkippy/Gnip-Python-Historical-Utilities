#!/usr/bin/env python
import requests
import json
import sys
import datetime
from gnip_historical_job import *

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
        if statusDict is None or statusDict["status"] == "error":
            self.status = 'Error retrieving Job status'
            if "reason" in statusDict:
                self.status += ": {}".format(statusDict["reason"])
            self.statusMessage = 'Please verify your connection parameters and network connection'
            self.title = "{} -- {}".format(self.status, self.statusMessage)
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
        else:
            res += 'Job URL: %s\n\n'%self.jobURL
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
        self.user_name = UN
        self.password = PWD
        self.baseUrl = baseUrl
        self.jobPars = jParsObj
        self.status = None  # status object created when job status is retrieved

    def acceptJob(self, jobURL):
        return self.xJob(jobURL, {"status":"accept"})

    def rejectJob(self, jobURL):
        return self.xJob(jobURL, {"status":"reject"})

    def xJob(self, jobURL, payload):
        res = None
        try:
            s = requests.Session()
            s.auth = (self.user_name, self.password)
            s.headers = {'content-type':'application/json'}
            res = s.put(jobURL, data=json.dumps(payload))
        except requests.exceptions.ConnectionError, e:
            print >> sys.stderr, "Server request failed with message {}".format(e)
        except requests.exceptions.HTTPError, e:
            print >> sys.stderr, "Server request failed with message {}".format(e)
        if res is not None and res.status_code == 200:
            return "Job {}ed successfully.".format(payload["status"])
        else:
            return "Request failed with response code ({}): {}".format(res.status_code, res.text)

    def createJob(self):
        res = None
        try:
            s = requests.Session()
            s.auth = (self.user_name, self.password)
            s.headers = {'content-type':'application/json'}
            res = s.post(self.baseUrl + "jobs.json", data=str(self.jobPars))
        except requests.exceptions.ConnectionError, e:
            print >> sys.stderr, "Server request failed with message {}".format(e)
        except requests.exceptions.HTTPError, e:
            print >> sys.stderr, "Server request failed with message {}".format(e)
        return Status(res.json())

    def listJobs(self):
        """Generator of jobs from the server. Jobs are generated in order and include every status
        type. The number of items returned depends on the history in the server job log."""
        res = None
        try:
            s = requests.Session()
            s.auth = (self.user_name, self.password)
            res = s.get(self.baseUrl + "jobs.json")
        except requests.exceptions.ConnectionError, e:
            print >> sys.stderr, "Server request failed with message {}".format(e)
        except requests.exceptions.HTTPError, e:
            print >> sys.stderr, "Server request failed with message {}".format(e)
        if res is not None and "jobs" in res.json():
            for x in res.json()["jobs"]:
                yield Status(x)
        else:
            yield {"status": "Status Error: Server failed to return valid JSON object"}
        
    def getDataURLDict(self, URL):
        """Return job record data download urls for the specified job. The url proivided should be the 
        specific url with job id provided by the system and must be in the current job
        log. That is, the url must represent a valid job that would be retrieved with e.g. listJobs."""
        res = None
        try:
            s = requests.Session()
            s.auth = (self.user_name, self.password)
            res = s.get(URL)
        except requests.exceptions.ConnectionError, e:
            print >> sys.stderr, "Server request failed with message {}".format(e)
        except requests.exceptions.HTTPError, e:
            print >> sys.stderr, "Server request failed with message {}".format(e)
        if res is not None:
            return res.json()
        else:
            return {"status": "Status Error: Server failed to return valid JSON object"}

    def getJobStatusDict(self, jobURL = None):
        """Return job record for the specified job. The url proivided should be the 
        specific url with job id provided by the system and must be in the current job
        log. That is, the url must represent a valid job that would be retrieved with e.g. listJobs."""
        res = None
        if jobURL is None:
            try:
                jobURL = self.status.jobURL
            except:
                sys.stderr.write("No job specified.\n")
                return res
        try:
            s = requests.Session()
            s.auth = (self.user_name, self.password)
            res = s.get(jobURL)
        except requests.exceptions.ConnectionError, e:
            print >> sys.stderr, "Server request failed with message {}".format(e)
        except requests.exceptions.HTTPError, e:
            print >> sys.stderr, "Server request failed with message {}".format(e)
        if res is not None:
            return res.json()
        else:
            return {"status": "Status Error: Server failed to return valid JSON object"}

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
