"""
.. Copyright 2016 EMBL-European Bioinformatics Institute

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from urllib2 import Request, urlopen, URLError
from dmp import rest
import json

def ping(a, b):
    """
    Ping the defined end points to determine if they are valid services. The
    results are then logged and used by the DMP and other service when listing
    what end points are available. This allows for services to drop out and not
    have nodes pointing to those services until they come back.
    
    Parameters
    ----------
    a : str
        key for the registry dict
    b : dict
        'a' is the registry key
    """
    r = rest.rest()
    
    for service in b[str(a)]:
        req = Request(service["url"])
        status = "down"
        log = ""
        data = {}
        try:
            response = urlopen(req)
            log = response.code
            data = json.loads(response.read())
            response.close()
        except URLError, e:
            valid = False
            log = e.code
        
        if log == 200:
            status = "up"
        
        if r.is_service(service["name"]) == True:
            r.set_service_status(service["name"], status)
        else:
            description = data["description"] if data.has_key("description") else ""
            r.add_service(service["name"], service["url"], description, status)
        
        #print service["name"] + " - " + str(log)
