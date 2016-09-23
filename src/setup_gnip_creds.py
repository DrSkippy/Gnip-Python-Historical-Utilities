#!/usr/bin/env python
import sys
import os
import datetime
import getpass
# py2to3 compatability
try: input = raw_input
except NameError: pass
try:
    from ConfigParser import ConfigParser
    from ConfigParser import DuplicateSectionError
except ImportError:
    from configparser import ConfigParser
    from configparser import DuplicateSectionError
import shutil

config = ConfigParser()
config.read('./.gnip')
try:
	config.add_section('creds')
except DuplicateSectionError:
	overwrite = input("File ./.gnip already exists. Overwrite? (Y/n)")
	if overwrite.lower() not in ['y','yes','','yup','ye','yep','affirmative','yessir','yepums','si','oui','ok']:
		print("Exiting.")
		sys.exit()
	else:
		shutil.move("./.gnip","./.gnip.old")
		config = ConfigParser()
		config.read('./.gnip')
		config.add_section('creds')

un = input("Username: ")
config.set('creds', 'un', un)
pwd = ""
pwd1 = "not set"
while pwd != pwd1:
	pwd = getpass.getpass("Password: ")
	pwd1 = getpass.getpass("Password again: ")
config.set('creds', 'pwd', pwd)
config.add_section('endpoint')
an = input("Endpoint URL. Enter your Account Name (eg https://gnip-api.gnip.com/historical/powertrack/accounts/<account name>/): ")
config.set('endpoint', 'url', "https://gnip-api.gnip.com/historical/powertrack/accounts/%s/"%an)
config.add_section('tmp')
config.set('tmp','prevUrl', "")
with open("./.gnip","w") as f:
	config.write(f)
print("Done creating file ./.gnip")
print("Be sure to run:\nchmod og-w .gnip")
print("Configuration setup complete.")
print("\nUpdating path information in get_data_files.bash...")
currentPath = os.getcwd()
state = 0
with open("./get_data_files.bash","w") as outf:
    with open("./get_data_files.bash.orig","r") as inf:
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
os.chmod("./get_data_files.bash", 0o755)
print("Done.")

