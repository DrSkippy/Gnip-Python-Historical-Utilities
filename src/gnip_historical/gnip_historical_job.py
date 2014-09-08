#!/usr/bin/env python
import json
import sys
import datetime
import codecs
import re

DATE_RE = re.compile("[0-9]{4}.[0-9]{2}.[0-9]{2}.[0-9]{2}.[0-9]{2}.[0-9]{2}")
DATEFMT = "%Y-%m-%dT%H:%M:%S"
SHORT_DATEFMT = "%Y%m%d%H%M"
#
class JobParameters(object):
    """Represent the an historical job with setters, getters, validity checks and create the
    necessary JSON job description record for creating new historical jobs."""
    def __init__(self, title, jobDict = None, jobFileName = None):
        """Create a new historical job representation by parseing job description (JSON) from file
        or set up to building programatically"""
        # create the basic job json structure
        self.job = {
            "publisher": "twitter",
            "streamType": "track",
            "dataFormat": "activity-streams",
            "fromDate": None,
            "toDate": None,
            "title": title,
            "rules": []
            }
        # pass a job dict into object?
        if jobDict is not None:
            # over write default
            self.job = jobDict
        elif jobFileName is not None:
            # lastly, try to read json from file
            try:
                with codecs.open(jobFileName,"rb","utf-8") as tmpJobFile:
                    tmp = tmpJobFile.read()
                    try:
                        tmpJob = json.loads(tmp)
                        for test_key in self.job.keys():
                            if test_key not in tmpJob:
                                raise ValueError("Required fields missing ({})".format(test_key))
                        self.job = tmpJob
                    except ValueError, e:
                        sys.stderr.write("Failed to parse input JSON. (%s). Exiting.\n"%e)
                        sys.exit()
                self.setToDate(tmpJob["toDate"])
                self.setFromDate(tmpJob["fromDate"])
            except IOError,e:
                sys.stderr.write("Failed to open rules file. (%s)\n"%e)
        # Given title supercedes file title, otherwise, use give title
        if title is not None:
            self.setTitle(title)

    def writeToFile(self, jobFileName):
        """Write current configuration as a job file"""
        with codecs.open(jobFileName,"wb","utf-8") as tmpJobFile:
            tmpJobFile.write(str(self))

    def setTitle(self, t):
        """Set the job title"""
        self.job["title"] = t

    def getTitle(self):
        """Get the job title. If the job title is not set, give a default title
        containing the date and time for uniqueness."""
        if "title" not in self.job or self.job["title"] is None:
            self.setTitle("Project started %s"%datetime.datetime.now())
        return self.job["title"]

    def parseDate(self, d):
        """Parse incoming data record.  Okay to pass date object or string."""
        res = d
        if not isinstance(d, datetime.datetime):
            if "-" in d or ":" in d:
                dtstr = DATE_RE.search(d).group(0)
                res = datetime.datetime.strptime(dtstr, DATEFMT)
            else:
                res = datetime.datetime.strptime(d, SHORT_DATEFMT)
        return res

    def fmtDate(self, dateObj):
        """Format date string in required job record format"""
        return dateObj.strftime(SHORT_DATEFMT)
    
    def setFromDate(self, dateObj):
        """Set job starting date from date object or string"""
        self.fromDateObj = self.parseDate(dateObj)
        self.job["fromDate"] = self.fmtDate(self.fromDateObj)

    #def getFromDate(self):
    #    """Get the from date object"""
    #    return self.fromDateObj

    def setToDate(self, dateObj):
        """Set job ending date from date object or string"""
        self.toDateObj = self.parseDate(dateObj)
        self.job["toDate"] = self.fmtDate(self.toDateObj)

    #def getToDate(self):
    #    return self.toDateObj

    def duration(self):
        """Return the job duration as a delta_date object."""
        return self.fromDateObj-self.toDateObj

    def setOriginalDataFormat(self):
        self.job["dataFormat"] = "original"

    def setActivityDataFormat(self):
        self.job["dataFormat"] = "activity-streams"

    def setRules(self, ruleList):
        """Set rules from list of dictionaries or a JSON string representation of a list of rules.
        Dictionaries must contain "values" and may contain "tags" keys."""
        if type(ruleList) == type([]):
            self.job["rules"] = ruleList
        elif type(ruleList) == type("string"):
            try:
                self.job["rules"] = json.loads(ruleList)
            except ValueError, e:
                sys.stderr.write("Failed to set rules by parsing JSON string. (%s)\n"%e)
        else:
            sys.stderr.write("Failed to set rules. Check argument type is list of valid rules or string with valid JSON.\n")

    def addRule(self, rule, tag=None):
        """Add a rule to existing rules list."""
        if tag is not None:
            self.job["rules"].append({"value": rule, "tag": tag})
        else:
            self.job["rules"].append({"value": rule})

    #def addRuleList(self, ruleList):
    #    # ruleList is a list of dicts, over writes existing list
    #    self.job["rules"] = ruleList

    def __str__(self):
        if self.toDateObj > self.fromDateObj and self.job["rules"] != []:
            return json.dumps(self.job)
        else:
            raise ValueError("Check that fromdDate < toDate and that you have set valid rules.")

