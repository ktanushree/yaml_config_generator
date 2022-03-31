#!/usr/bin/env python
"""
YAML Config generator
Script expects CSV data file and Jinja template to create site specific YAML config files

Author: tkamath@paloaltonetworks.com

"""
import sys
import os
import argparse
import cloudgenix
import jinja2
from jinja2 import Template
import yaml
import json
import csv
import pandas as pd

SCRIPT_NAME = "YAML Config Generator"
SCRIPT_VERSION = "v1.0"


# Import CloudGenix Python SDK
try:
    import cloudgenix
except ImportError as e:
    cloudgenix = None
    sys.stderr.write("ERROR: 'cloudgenix' python module required. (try 'pip install cloudgenix').\n {0}\n".format(e))
    sys.exit(1)

# Check for cloudgenix_settings.py config file in cwd.
sys.path.append(os.getcwd())
try:
    from cloudgenix_settings import CLOUDGENIX_AUTH_TOKEN

except ImportError:
    # if cloudgenix_settings.py file does not exist,
    # Get AUTH_TOKEN/X_AUTH_TOKEN from env variable, if it exists. X_AUTH_TOKEN takes priority.
    if "X_AUTH_TOKEN" in os.environ:
        CLOUDGENIX_AUTH_TOKEN = os.environ.get('X_AUTH_TOKEN')
    elif "AUTH_TOKEN" in os.environ:
        CLOUDGENIX_AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
    else:
        # not set
        CLOUDGENIX_AUTH_TOKEN = None

try:
    # Also, separately try and import USERNAME/PASSWORD from the config file.
    from cloudgenix_settings import CLOUDGENIX_USER, CLOUDGENIX_PASSWORD

except ImportError:
    # will get caught below
    CLOUDGENIX_USER = None
    CLOUDGENIX_PASSWORD = None


# Handle differences between python 2 and 3. Code can use text_type and binary_type instead of str/bytes/unicode etc.
if sys.version_info < (3,):
    text_type = unicode
    binary_type = str
else:
    text_type = str
    binary_type = bytes


def clean_exit(cgx_session):
    cgx_session.get.logout()
    sys.exit()


def go():
    """
    Stub script entry point. Authenticates CloudGenix SDK, and gathers options from command line to run do_site()
    :return: No return
    """
    ############################################################################
    # Begin Script, parse arguments.
    ############################################################################

    parser = argparse.ArgumentParser(description="{0} ({1})".format(SCRIPT_NAME, SCRIPT_VERSION))

    # Standard CloudGenix script switches.
    controller_group = parser.add_argument_group('API', 'These options change how this program connects to the API.')
    controller_group.add_argument("--controller", "-C",
                                  help="Controller URI, ex. https://api.elcapitan.cloudgenix.com",
                                  default=None)

    login_group = parser.add_argument_group('Login', 'These options allow skipping of interactive login')
    login_group.add_argument("--email", "-E", help="Use this email as User Name instead of cloudgenix_settings.py "
                                                   "or prompting",
                             default=None)
    login_group.add_argument("--password", "-PW", help="Use this Password instead of cloudgenix_settings.py "
                                                       "or prompting",
                             default=None)
    login_group.add_argument("--insecure", "-I", help="Do not verify SSL certificate",
                             action='store_true',
                             default=False)
    login_group.add_argument("--noregion", "-NR", help="Ignore Region-based redirection.",
                             dest='ignore_region', action='store_true', default=False)

    debug_group = parser.add_argument_group('Debug', 'These options enable debugging output')
    debug_group.add_argument("--sdkdebug", "-D", help="Enable SDK Debug output, levels 0-2", type=int,
                             default=0)

    config_group = parser.add_argument_group('Config', 'These options are to provide Config parameters')
    config_group.add_argument("--csvfile", "-F", help="CSV file name. Please include the entire path",default=None)
    config_group.add_argument("--jinjafile", "-J", help="Jinja template. Please include the entire path",default=None)
    config_group.add_argument("--outputdir", "-O", help="Output directory to store YAML config files",default=None)
    config_group.add_argument("--sitename", "-S", help="CSV column name for extracting YAML file name. Typically, YAML config files are site specific and named after the site.",default=None)

    ############################################################################
    # Parse arguments provided via CLI & Validate them
    ############################################################################
    args = vars(parser.parse_args())
    sdk_debuglevel = args["sdkdebug"]
    csvfile = args["csvfile"]
    template_file = args["jinjafile"]
    outputdir = args["outputdir"]
    sitename = args["sitename"]

    if not os.path.exists(csvfile):
        print("ERR: CSV Data file not found. Please provide the entire path")
        sys.exit()

    if not os.path.exists(template_file):
        print("ERR: Jinja Template not found. Please provide the entire path")
        sys.exit()

    if not os.path.exists(outputdir):
        print("ERR: Output Directory not found. Please provide a valid path")
        sys.exit()
    ############################################################################
    # Instantiate API & Login
    ############################################################################
    cgx_session = cloudgenix.API(controller=args["controller"], ssl_verify=False)
    print("{0} v{1} ({2})\n".format(SCRIPT_NAME, cloudgenix.version, cgx_session.controller))

    # login logic. Use cmdline if set, use AUTH_TOKEN next, finally user/pass from config file, then prompt.
    # figure out user
    if args["email"]:
        user_email = args["email"]
    elif CLOUDGENIX_USER:
        user_email = CLOUDGENIX_USER
    else:
        user_email = None

    # figure out password
    if args["pass"]:
        user_password = args["pass"]
    elif CLOUDGENIX_PASSWORD:
        user_password = CLOUDGENIX_PASSWORD
    else:
        user_password = None

    # check for token
    if CLOUDGENIX_AUTH_TOKEN and not args["email"] and not args["pass"]:
        cgx_session.interactive.use_token(CLOUDGENIX_AUTH_TOKEN)
        if cgx_session.tenant_id is None:
            print("AUTH_TOKEN login failure, please check token.")
            sys.exit()

    else:
        while cgx_session.tenant_id is None:
            cgx_session.interactive.login(user_email, user_password)
            # clear after one failed login, force relogin.
            if not cgx_session.tenant_id:
                user_email = None
                user_password = None

    ############################################################################
    # Read CSV Data & Jinja Template
    ############################################################################
    with open(template_file) as jinjafd:
        print("INFO: Reading jinja template")
        template = Template(jinjafd.read())

    print("INFO: Reading CSV data source")
    csvdata = pd.read_csv(csvfile)

    ############################################################################
    # Generate YAML Config files
    ############################################################################
    columns = list(csvdata.columns)
    if sitename in columns:
        print("INFO: Generating YAML Config files")
        for i, row in csvdata.iterrows():
            print("\t{}".format(row[sitename]))
            config = {}
            for item in columns:
                if item == sitename:
                    sitename = row[item]

                config[item] = row[item]

            siteconfig = template.render(config)

            filename = "{}/{}.yml".format(outputdir, sitename)
            print("\tSaving config: {}".format(filename))
            f = open(filename, "w")
            f.write(siteconfig)
            f.close()

    else:
        print("ERR: Invalid column name for sitename: {}".format(sitename))
        clean_exit(cgx_session)

    ############################################################################
    # Generate YAML Config files
    ############################################################################
    print("INFO: Logging out")
    clean_exit(cgx_session)

if __name__ == "__main__":
    go()
