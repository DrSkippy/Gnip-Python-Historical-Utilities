# Gnip Python Historical Utilities

Python modules and associated command-line utilities for use with the [Gnip](http://gnip.com/) [Historical PowerTrack](http://support.gnip.com/apis/historical_api/) API.

The process for launching and retrieveing data for an historical historical job 
requires only a few steps:

- set up credentials
- create job
- retrieve and review job quote
- accept or reject job
- download data files list
- download data

Utilities are included to assist with each step.

------

Setup utility
=============
First, set up your Gnip credentials.  There is a simple utility to create the local credential 
file named ".gnip".

    $ ./setup_gnip_creds.py 
    Username: shendrickson@gnip.com    
    Password: 
    Password again: 
    Endpoint URL. Enter your Account Name (eg https://historical.gnip.com:443/accounts/<account name>/): shendrickson
    Done creating file ./.gnip
    Be sure to run:
    chmod og-w .gnip
        
    $ chmod og-w .gnip

You may wish to run these utilities from other directory locations. If so, be sure the export an
updated ``PYTHONPATH``,

    $ export PYTHONPATH=${PYTHONPATH}:path-to-gnip-python-historical-utilities

You can, alternatively, set up a symlink called ``data`` within the repository directory, pointing to your  
data destination.


Create job
==========
Create a job description by editing the example JSON file provided (``bieber_job1.json``).

You will end up with a single JSON record like this (see GNIP documentation for option 
details). the fromDate and toDate are in the format YYYYmmddHHMM:

    {
        "dataFormat" : "activity-streams",
        "fromDate" : "201201010000",
        "toDate" : "201201010001"
        "publisher" : "twitter",
        "rules" : 
        [
            {
                "tag" : "bestRuleEver",
                "value" : "bieber"
            }
        ],
        "streamType" : "track",
        "title" : "BieberJob1",
    }

To create the job,

    $ ./create_job.py -f./bieber_job1.json -t "Social Data Phenoms - Bieber"

The response is the JSON record returned by the server. It will describe the job (including
JobID and the JobURL, or any error messages.

To get help,

    $ ./create_job.py -h
    Usage: create_job.py [options]

    Options:
      -h, --help            show this help message and exit
      -u URL, --url=URL     Job url.
      -l, --prev-url        Use previous Job URL (only from this configuration
                            file.).
      -v, --verbose         Detailed output.
      -f FILENAME, --filename=FILENAME
                            File defining job (JSON)
      -t TITLE, --title=TITLE
                            Title of project, this title supercedes title in file.


List jobs, get quotes, status
=============================

    $ ./list_jobs.py -h
    Usage: list_jobs.py [options]

    Options:
      -h, --help            show this help message and exit
      -u URL, --url=URL     Job url.
      -l, --prev-url        Use previous Job URL (only from this configuration
                            file.).
      -v, --verbose         Detailed output.
      -d SINCEDATESTRING, --since-date=SINCEDATESTRING
                            Only list jobs after date, (default
                            2012-01-01T00:00:00)

For example, I have three completed jobs, a Gnip job, a Bieber job and a SXSW 
job for which data is avaiable.

    $  ./list_jobs.py 
    #########################
    TITLE:     GNIP2012
    STATUS:    finished
    PROGRESS:  100.0 %
    JOB URL:   https://historical.gnip.com:443/accounts/shendrickson/publishers/twitter/historical/track/jobs/eeh2vte64.json
    #########################
    TITLE:     Justin Bieber 2009
    STATUS:    finished
    PROGRESS:  100.0 %
    JOB URL:   https://historical.gnip.com:443/accounts/shendrickson/publishers/twitter/historical/track/jobs/j5epx4e5c3.json
    #########################
    TITLE:     SXSW2010-2012
    STATUS:    finished
    PROGRESS:  100.0 %
    JOB URL:   https://historical.gnip.com:443/accounts/shendrickson/publishers/twitter/historical/track/jobs/sbxff05b8d.json


To see detailed information or download data filelist, 
specify URL with -u or add -v flag (``data_files.txt`` contains 
only URLs from last job in list)


Accept / reject job
==================
After a job is quoted, you can accept or reject the job.  The job will not start until it is accepted.

    $ ./accept_job -u https://historical.gnip.com:443/accounts/shendrickson/publishers/twitter/historicals/track/jobs/c9pe0day6h.json

or 

    $ ./reject_job -u https://historical.gnip.com:443/accounts/shendrickson/publishers/twitter/historicals/track/jobs/c9pe0day6h.json


Download URLs of data files
===========================
To retrieve the file locations for the data files this job created on S3, pass 
the job URL with the -u flag (or if you used -u for this job previously, just use -l--see help),

    $  ./list_jobs.py -u  https://historical.gnip.com:443/accounts/shendrickson/publishers/twitter/historical/track/jobs/sbxff05b8d.json
    #########################
    TITLE:     SXSW2010-2012
    STATUS:    finished
    PROGRESS:  100.0 %
    JOB URL:   https://historical.gnip.com:443/accounts/shendrickson/publishers/twitter/historical/track/jobs/sbxff05b8d.json

    RESULT:
     Job completed at ........ 2012-09-01 04:35:23
     No. of Activities ....... -1
     No. of Files ............ -1
     Files size (MB) ......... -1
     Data URL ................ https://historical.gnip.com:443/accounts/shendrickson/publishers/twitter/historical/track/jobs/sbxff05b8d/results.json
    DATA SET:
     No. of URLs ............. 131,211
     File size (bytes)........ 2,151,308,466
     Files (URLs) ............ https://archive.replay.historicals.review.s3.amazonaws.com/historicals/twitter/track/activity-streams/shendrickson/2012/08/28/20100101-20120815_sbxff05b8d/2010/01/01/00/00_activities.json.gz?AWSAccessKeyId=AKIAJ7O2S22DN2NDN7UQ&Expires=1349066046&Signature=hDSc0a%2BRQeG%2BknaSAWpzSUoM1F0%3D
    https://archive.replay.historicals.review.s3.amazonaws.com/historicals/twitter/track/activity-streams/shendrickson/2012/08/28/20100101-20120815_sbxff05b8d/2010/01/01/00/10_activities.json.gz?AWSAccessKeyId=AKIAJ7O2S22DN2NDN7UQ&Expires=1349066046&Signature=DOZlXKuMByv5uKgmw4QrCOpmEVw%3D
    https://archive.replay.historicals.review.s3.amazonaws.com/historicals/twitter/track/activity-streams/shendrickson/2012/08/28/20100101-20120815_sbxff05b8d/2010/01/01/00/20_activities.json.gz?AWSAccessKeyId=AKIAJ7O2S22DN2NDN7UQ&Expires=1349066046&Signature=X4SFTxwM2X9Y7qwgKCwG6fH8h7w%3D
    https://archive.replay.historicals.review.s3.amazonaws.com/historicals/twitter/track/activity-streams/shendrickson/2012/08/28/20100101-20120815_sbxff05b8d/2010/01/01/00/30_activities.json.gz?AWSAccessKeyId=AKIAJ7O2S22DN2NDN7UQ&Expires=1349066046&Signature=WVubKurX%2BAzYeZLX9UnBamSCrHg%3D
    https://archive.replay.historicals.review.s3.amazonaws.com/historicals/twitter/track/activity-streams/shendrickson/2012/08/28/20100101-20120815_sbxff05b8d/2010/01/01/00/40_activities.json.gz?AWSAccessKeyId=AKIAJ7O2S22DN2NDN7UQ&Expires=1349066046&Signature=OG9ygKlXNxFvJLlAEWi3hes5yyw%3D
    ...

    Writing files to data_files.txt...

Filenames for the 131K files created on S3 by the job have been downloaded to a file in 
the local directory, ``./data_files.txt``.


Download data files
===================

To retrieve this data use the utility,

    $ ./get_data_files.bash
    ...

This will lauch up to 8 simultaneousl cUrl connections to S3 to download the files 
into a local ``./data/year/month/day/hour/...`` directory tree (see ``name_mangle.py`` for details).

The module ``gnip_historical.py`` provides additional functionality you can access programatically.

==
Gnip-Python-Historical-Utilities by Scott Hendrickson is licensed under a Creative Commons Attribution-ShareAlike 3.0 Unported License. This work is licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/.



