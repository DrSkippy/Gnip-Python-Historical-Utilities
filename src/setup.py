from distutils.core import setup

setup(
    name='gnip-historical',
    version='0.4.0',
    author='Scott Hendrickson, Brian Lehman, Josh Montague',
    author_email='scott@drskippy.net',
    packages=['gnip_historical'],
    scripts=['create_job.py', 'accept_job.py','reject_job.py', 'list_jobs.py'],
    url='http://pypi.python.org/pypi/gnip-historical/',
    license='LICENSE.txt',
    description='Gnip Historical libarary and command scripts.',
    long_description=open('README').read(),
)
