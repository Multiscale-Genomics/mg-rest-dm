# mg-rest-dm
RESTful access to the DMP

# Requirements
- Mongo DB 3.2
- Python 2.7.10+
- pyenv
- pyenv virtualenv
- Python Modules:
  - DMP
  - Flask
  - Flask-Restful
  - Waitress

# Installation
Cloneing from GitHub:
```
git clone https://github.com/Multiscale-Genomics/mg-rest-dm.git
```
To get this to be picked up by pip if part of a webserver then:
```
pip install --editable .
```
This should install the required packages listed in the `setup.py` script.


Installation via pip:
```
pip install git+https://github.com/Multiscale-Genomics/mg-rest-dm.git
```

# Configuration files
Requires a file with the name `mongodb.cnf` with the following parameters to define the MongoDB server:
```
[dmp]
host = localhost
port = 27017
user = testuser
pass = test123
db = dmp
ftp_root = ftp://ftp.multiscalegenomics.eu/test
```

# Setting up a server
```
git clone https://github.com/Multiscale-Genomics/mg-rest-dm.git

cd mg-rest-dm
pyenv virtualenv 2.7.12 mg-rest-dm
pyenv activate mg-rest-dm
pip install git+https://github.com/Multiscale-Genomics/mg-dm-api.git
pip install -e .
pip deactivate
```
Starting the service:
```
nohup ${PATH_2_PYENV}/versions/2.7.12/envs/mg-rest-dm/bin/waitress-serve --listen=127.0.0.1:5001 rest.app:app &
```

# RESTful API
## List end points
Request:
```
wget http://127.0.0.1:5001/api/dmp
```
Returns:
```
{"_links": {"_self": "http://ves-ebi-64.ebi.ac.uk/api", "DMP" : "http://ves-ebi-64.ebi.ac.uk/api/dmp"}}
```

## List tracks for a given user
Parameters:
- user_id - Unique user token

Request:
```
wget http://127.0.0.1:5001/api/dmp/getTracks?user_id=<user_id>
```
Returns:
```
{"files": [{"data_type": "HiC", "file_type": "hdf5", "creation_time": "2016-12-13 09:03:23.082223", "taxon_id": 9606, "meta_data": {}, "source_id": [], "_id": "584fb95b10753109a257081e", "file_path": "ftp://ftp.multiscalegenomics.eu/test/584fb95b10753109a257081e/dmp/rao2014.hdf5"}], "_links": {"self": "http://127.0.0.1:5001/api/dmp/getTracks"}}
```

## List file history
Parameters:
- user_id - Unique user token
- file_id - File identifier

Request:
```
wget http://127.0.0.1:5001/api/dmp/getTrackHistory?user_id=<user_id>&file_id=<file_id>
```
Returns:
```

```

## ping
Request:
```
wget http://127.0.0.1:5001/api/dmp/ping
```
Returns:
```
{"status": "ready", "description": "Main process for checking REST APIs are available", "license": "Apache 2.0", "author": "Mark McDowall", "version": "v0.0", "name": "Service"}
```

