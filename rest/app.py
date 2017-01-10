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

from flask import Flask, make_response, request
from flask_restful import Api, Resource

from dmp import dmp

import logging, os
logging.basicConfig()

app = Flask(__name__)


class GetEndPoints(Resource):
    """
    Class to handle the http requests for returning information about the end
    points
    """
    
    def get(self):
        return {
            '_links': {
                '_self': request.base_url,
                '_getTracks': request.url_root + 'api/dmp/getTracks',
                '_getTrackHistory': request.url_root + 'api/dmp/getTrackHistory',
                '_ping': request.url_root + 'api/dmp/ping',
                '_parent': request.url_root + 'api'
            }
        }


class GetTracks(Resource):
    """
    Class to handle the http requests for retrieving the list of files for a
    given user handle
    """
    
    def usage(self, error_message, status_code, parameters = {}):
        usage = {
                    'link' : request.url,
                    'parameters' : {
                        'user_id' : ['User ID', 'str', 'REQUIRED'],
                        'file_id' : ['File ID', 'str', 'REQUIRED'],
                    }
                }
        message = {
                      'usage' : usage,
                      'status_code' : status_code
                  }

        if len(parameters) > 0:
            message['provided_parameters'] = parameters
        
        if error_message != None:
            message['error'] = error_message

        return message
    
    def get(self):
        cnf_loc=os.path.dirname(os.path.abspath(__file__)) + '/mongodb.cnf'
        da = dmp(cnf_loc)
        
        # TODO Placeholder code
        user_id = request.args.get('user_id')
        file_id = request.args.get('file_id')
        
        params = [user_id, file_id]

        # Display the parameters available
        if sum([x is None for x in params]) == len(params):
            return self.usage(None, 200)
        
        # ERROR - one of the required parameters is NoneType
        if sum([x is not None for x in params]) != len(params):
            return self.usage('MissingParameters', 400, {'user_id' : user_id, 'file_id' : file_id}), 400
        
        return {
            '_links': {
                'self': request.base_url,
            },
            'files': files
        }


class GetTrackHistory(Resource):
    """
    Class to handle the http requests for retrieving the list of file history of
    a given file for a given user handle
    """
    
    def usage(self, error_message, status_code, parameters = {}):
        usage = {
                    'link' : request.url,
                    'parameters' : {
                        'user_id' : ['User ID', 'str', 'REQUIRED'],
                        'file_id' : ['File ID', 'str', 'REQUIRED'],
                    }
                }
        message = {
                      'usage' : usage,
                      'status_code' : status_code
                  }

        if len(parameters) > 0:
            message['provided_parameters'] = parameters
        
        if error_message != None:
            message['error'] = error_message

        return message
    
    def get(self):
        cnf_loc=os.path.dirname(os.path.abspath(__file__)) + '/mongodb.cnf'
        da = dmp(cnf_loc)
        
        # TODO Placeholder code
        user_id = request.args.get('user_id')
        file_id = request.args.get('file_id')
        
        params = [user_id, file_id]

        # Display the parameters available
        if sum([x is None for x in params]) == len(params):
            return self.usage(None, 200)
        
        # ERROR - one of the required parameters is NoneType
        if sum([x is not None for x in params]) != len(params):
            return self.usage('MissingParameters', 400, {'user_id' : user_id, 'file_id' : file_id}), 400
        
        files = da.get_files_history(file_id)
        
        return {
            '_links': {
                'self': request.base_url,
            },
            'history_files': files
        }

class ping(Resource):
    """
    Class to handle the http requests to ping a service
    """
    
    def get(self):
        import release
        res = {
            "status":  "ready",
            "version": release.__version__,
            "author":  release.__author__,
            "license": release.__license__,
            "name":    release.__rest_name__,
            "description": release.__description__
        }
        return res

# TODO
# For the services where there needs to be an extra layer (adjacency lists),
# then there needs to be a way of forwarding for this. But the majority of
# things can be redirected to the raw files for use as a track.
#

"""
Define the URIs and their matching methods
"""
api = Api(app)

#   List the available end points for this service
api.add_resource(GetEndPoints, "/api/dmp", endpoint='dmp_root')

#   List the available species for which there are datasets available
api.add_resource(GetTracks, "/api/dmp/getTracks", endpoint='tracks')

#   List file history
api.add_resource(GetTrackHistory, "/api/dmp/getTrackHistory", endpoint='trackHistory')

#   Service ping
api.add_resource(ping, "/api/dmp/ping", endpoint='dmp-ping')


"""
Initialise the server
"""
if __name__ == "__main__":
    app.run(port=5001, debug=True, use_reloader=False)
