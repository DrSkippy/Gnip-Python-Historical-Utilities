#!/usr/bin/env python
import sys
import os
import datetime
import getpass
import ConfigParser
import shutil

config = ConfigParser.ConfigParser()
config.read('./.gnip')
try:
	config.add_section('creds')
except ConfigParser.DuplicateSectionError:
	overwrite = raw_input("File ./.gnip already exists. Overwrite? (Y/n)")
	if overwrite.lower() not in ['y','yes','','yup','ye','yep','affirmative','yessir','yepums','si','oui','ok']:
		print "Exiting."
		sys.exit()
	else:
		shutil.move("./.gnip","./.gnip.old")
		config = ConfigParser.ConfigParser()
		config.read('./.gnip')
		config.add_section('creds')

un = raw_input("Username: ")
config.set('creds', 'un', un)
pwd = ""
pwd1 = "not set"
while pwd <> pwd1:
	pwd = getpass.getpass("Password: ")
	pwd1 = getpass.getpass("Password again: ")
config.set('creds', 'pwd', pwd)
config.add_section('endpoint')
an = raw_input("Endpoint URL. Enter your Account Name (eg https://historical.gnip.com/accounts/<account name>/): ")
config.set('endpoint', 'url', "https://historical.gnip.com/accounts/%s/"%an)
config.add_section('tmp')
config.set('tmp','prevUrl', "")
with open("./.gnip","wb") as f:
	config.write(f)
print "Done creating file ./.gnip"
print "Be sure to run:\nchmod og-w .gnip"
print "Configuration setup complete."
print "\nUpdating path information in get_data_files.bash..."
currentPath = os.getcwd()
state = 0
with open("./get_data_files.bash","wb") as outf:
    with open("./get_data_files.bash.orig","rb") as inf:
        for line in inf:
            newline = line
            if line.startswith("AUTOPATH="):
                state = 1
                newline = "# Auto updated: %s\n# %s"%(datetime.datetime.now(), line)
            else:
                if state == 1:
                    newline = "AUTOPATH=%s\n"%currentPath + line
                    state = 2
            outf.write(newline)
os.chmod("./get_data_files.bash", 0755 )
print "Done."

