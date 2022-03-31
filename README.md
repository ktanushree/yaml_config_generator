# Prisma SDWAN Config Generator
This script is used to generate YAML config files from a CSV data source and a Jinja template

#### Synopsis
This script is used to generate YAML config files from a CSV data source and a Jinja template


#### Requirements
* Active Prisma SDWAN Account
* Python >=3.6
* Pandas
* jinja2

#### License
MIT

#### Installation:
 - **Github:** Download files to a local directory, manually run `yaml_config_generator.py`. 

### Examples of usage:
```
./yaml_config_generator.py -F csvfile.csv -J jinjatemplate.jinja2 -O /Users/tkamath/configs -S site_name
```


#### Help Text:
```angular2
TanushreeKamath:yaml_config_generator tkamath$ ./yaml_config_generator.py -h
usage: configgen.py [-h] [--controller CONTROLLER] [--email EMAIL] [--password PASSWORD] [--insecure] [--noregion] [--sdkdebug SDKDEBUG] [--csvfile CSVFILE] [--jinjafile JINJAFILE] [--outputdir OUTPUTDIR] [--sitename SITENAME]

YAML Config Generator (v1.0)

optional arguments:
  -h, --help            show this help message and exit

API:
  These options change how this program connects to the API.

  --controller CONTROLLER, -C CONTROLLER
                        Controller URI, ex. https://api.elcapitan.cloudgenix.com

Login:
  These options allow skipping of interactive login

  --email EMAIL, -E EMAIL
                        Use this email as User Name instead of cloudgenix_settings.py or prompting
  --password PASSWORD, -PW PASSWORD
                        Use this Password instead of cloudgenix_settings.py or prompting
  --insecure, -I        Do not verify SSL certificate
  --noregion, -NR       Ignore Region-based redirection.

Debug:
  These options enable debugging output

  --sdkdebug SDKDEBUG, -D SDKDEBUG
                        Enable SDK Debug output, levels 0-2

Config:
  These options are to provide Config parameters

  --csvfile CSVFILE, -F CSVFILE
                        CSV file name. Please include the entire path
  --jinjafile JINJAFILE, -J JINJAFILE
                        Jinja template. Please include the entire path
  --outputdir OUTPUTDIR, -O OUTPUTDIR
                        Output directory to store YAML config files
  --sitename SITENAME, -S SITENAME
                        CSV column name for extracting YAML file name. Typically, YAML config files are site specific and named after the site.

TanushreeKamath:yaml_config_generator tkamath$ 
```

#### Version
| Version | Build | Changes |
| ------- | ----- | ------- |
| **1.0.0** | **b1** | Initial Release. |


#### For more info
 * Get help and additional Prisma SDWAN Documentation at <https://docs.paloaltonetworks.com/prisma/prisma-sd-wan.html>
