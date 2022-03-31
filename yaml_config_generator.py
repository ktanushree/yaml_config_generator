#!/usr/bin/env python
"""
YAML Config generator
Script expects CSV data file and Jinja template to create site specific YAML config files

Author: tkamath@paloaltonetworks.com
"""
import sys
import os
import argparse
import jinja2
from jinja2 import Template
import yaml
import json
import csv
import pandas as pd

SCRIPT_NAME = "YAML Config Generator"
SCRIPT_VERSION = "v1.0"


# Handle differences between python 2 and 3. Code can use text_type and binary_type instead of str/bytes/unicode etc.
if sys.version_info < (3,):
    text_type = unicode
    binary_type = str
else:
    text_type = str
    binary_type = bytes


def go():

    ############################################################################
    # Begin Script, parse arguments.
    ############################################################################

    parser = argparse.ArgumentParser(description="{0} ({1})".format(SCRIPT_NAME, SCRIPT_VERSION))

    config_group = parser.add_argument_group('Config', 'These options are to provide Config parameters')
    config_group.add_argument("--csvfile", "-F", help="CSV file name. Please include the entire path",default=None)
    config_group.add_argument("--jinjafile", "-J", help="Jinja template. Please include the entire path",default=None)
    config_group.add_argument("--outputdir", "-O", help="Output directory to store YAML config files",default=None)
    config_group.add_argument("--sitename", "-S", help="CSV column name for extracting YAML file name. Typically, YAML config files are site specific and named after the site.",default=None)

    ############################################################################
    # Parse arguments provided via CLI & Validate them
    ############################################################################
    args = vars(parser.parse_args())
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
        sys.exit()

    ############################################################################
    # Generate YAML Config files
    ############################################################################
    print("INFO: Logging out")
    sys.exit()

if __name__ == "__main__":
    go()
