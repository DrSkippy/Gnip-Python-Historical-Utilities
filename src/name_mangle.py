#!/usr/bin/env python
import sys
import re
dateRE = re.compile("[0-9]{4}/[0-9]{2}/[0-9]{2}/[0-9]{2}/[0-9]{2}_")
nameRE = re.compile("[0-9]{8}-[0-9]{8}_[0-9a-z]+")
# file name retain date-based-path elements for downloaded files
for line in sys.stdin:
    # https://archive.replay.snapshots.review.s3.amazonaws.com/snapshots/twitter/track/activity-streams/shendrickson/2012/08/13/20090101-20100101_c9pe0day6h/2009/12/31/23/50_activities.json.gz?AWSAccessKeyId=AKIAI3ZYYXK57KIWDGHQ&Expires=1347654202&Signature=ej8iMVWVfYZE6qVGi%2FU%2FY5clnb0%3D
    infile = line.split("?")[0]
    # https://archive.replay.snapshots.review.s3.amazonaws.com/snapshots/twitter/track/activity-streams/shendrickson/2012/08/13/20090101-20100101_c9pe0day6h/2009/12/31/23/50_activities.json.gz
    sys.stdout.write("{} {}\n".format(line.rstrip('\n'), dateRE.search(infile).group(0) + nameRE.search(infile).group(0) + ".json.gz") )
