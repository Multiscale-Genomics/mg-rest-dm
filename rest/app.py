"""
.. Copyright 2017 EMBL-European Bioinformatics Institute

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

import json

import logging, os
logging.basicConfig()

app = Flask(__name__)


def usage(self, error_message, status_code,
    parameters_required = [], parameters_provided = {}):
    """
    Descrition of the basic usage pattern for GET
    """
    parameters = {
        'user_id' : ['User ID', 'str', 'REQUIRED'],
        'file_id' : ['File ID', 'str', 'REQUIRED'],
        'chrom'   : ['Chromosome', 'str', 'REQUIRED'],
        'start'   : ['Start', 'int', 'REQUIRED'],
        'end'   : ['End', 'int', 'REQUIRED'],
        'type' : ['add_meta|remove_meta', 'str', 'REQUIRED']
    }
    
    used_param = {k : parameters[k] for k in parameters_required if k in parameters}

    usage = {
                '_links' : {
                    '_self' : request.base_url,
                    '_parent' : request.url_root + 'mug/api/dmp'
                },
                'parameters' : used_param
            }
    message = {
                  'usage' : usage,
                  'status_code' : status_code
              }

    if len(parameters_provided) > 0:
        message['provided_parameters'] = parameters_provided
    
    if error_message != None:
        message['error'] = error_message

    return message

class EndPoints(Resource):
    """
    Class to handle the http requests for returning information about the end
    points
    """
    
    def get(self):
        return {
            '_links': {
                '_self': request.base_url,
                '_getTrack': request.url_root + 'mug/api/dmp/track',
                '_getTracks': request.url_root + 'mug/api/dmp/tracks',
                '_getTrackHistory': request.url_root + 'mug/api/dmp/trackHistory',
                '_ping': request.url_root + 'mug/api/dmp/ping',
                '_parent': request.url_root + 'mug/api'
            }
        }


class Track(Resource):
    """
    Class to handle the http requests for retrieving the data from a track file.
    This class is able to handle big[Bed|Wig] file and serve back the matching 
    region in the relevant format.
    """

    def get(self):
        """
        """
        cnf_loc=os.path.dirname(os.path.abspath(__file__)) + '/mongodb.cnf'
        da = dmp(cnf_loc)
        
        # TODO Placeholder code
        user_id = request.args.get('user_id')
        file_id = request.args.get('file_id')
        chrom = request.args.get('chrom')
        start = request.args.get('start')
        end   = request.args.get('end')
        
        params_requried = ['user_id', 'file_id', 'chrom', 'start', 'end']
        params = [user_id, file_id, chrom, start, end]

        # Display the parameters available
        if sum([x is None for x in params]) == len(params):
            return self.usage(None, 200)
        
        # ERROR - one of the required parameters is NoneType
        if sum([x is not None for x in params]) != len(params):
            return self.usage('MissingParameters', 400, params_requried, {'user_id' : user_id})

        file_obj = da.get_file_by_id(user_id, file_id, rest=True)

        output_str = ''
        if file_obj['file_type'] in ['bed', 'bigbed']:
            bbr = da.reader.bigbed_reader(user_id, file_id)
            output_str = bbr.get_range(chromosome, start, end, 'bed')
        elif file_obj['file_type'] in ['wig', 'bigwig']:
            bwr = da.reader.bigwig_reader(user_id, file_id)
            output_str = bwr.get_range(chromosome, start, end, 'wig')

        return output_str

    def post(self):
        """
        Add a new file to the DM API
        """
        cnf_loc=os.path.dirname(os.path.abspath(__file__)) + '/mongodb.cnf'
        da = dmp(cnf_loc)
        
        new_track = json.loads(request.data)
        user_id = new_track['user_id'] if 'user_id' in new_track else None
        file_path = new_track['file_path'] if 'file_path' in new_track else None
        file_type = new_track['file_type'] if 'file_type' in new_track else None
        data_type = new_track['data_type'] if 'data_type' in new_track else None
        taxon_id = new_track['taxon_id'] if 'taxon_id' in new_track else None
        source_id = new_track['source_id'] if 'source_id' in new_track else None
        meta_data = new_track['meta_data'] if 'meta_data' in new_track else None
        compressed = new_track['compressed'] if 'compressed' in new_track else None

        params_required = ['user_id', 'file_path', 'file_type', 'data_type', 'taxon_id', 'source_id', 'meta_data']
        params = [user_id, file_path, file_type, data_type, taxon_id, source_id, meta_data]

        # ERROR - one of the required parameters is NoneType
        if sum([x is not None for x in params]) != len(params):
            return self.usage('MissingParameters', 400, params_required, {'user_id' : user_id})

        new_track = json.loads(request.data)
        
        file_id = da.set_file(user_id,
            file_path,
            file_type,
            data_type,
            taxon_id,
            compressed,
            source_id,
            meta_data
        )

        return file_id

    def put(self):
        """
        Update meta data
        """
        cnf_loc=os.path.dirname(os.path.abspath(__file__)) + '/mongodb.cnf'
        da = dmp(cnf_loc)

        d = json.loads(request.data)
        user_id = d['user_id']
        file_id = d['file_id']

        params_requried = ['user_id', 'file_id', 'type']
        
        if d['type'] == 'add_meta':
            for k in d['meta_data']:
                result = da.add_file_metadata(file_id, k, d['meta_data'][k])
        elif d['type'] == 'remove_meta':
            for k in d['meta_data']:
                result = da.remove_file_metadata(file_id, k)
        else:
            return self.usage('MissingMetaDataParameters', 400, params_required, {'type' : ['add_meta', 'remove_meta']})
        return d

    def delete(self):
        """
        Remove a file from the DM API
        """
        cnf_loc=os.path.dirname(os.path.abspath(__file__)) + '/mongodb.cnf'
        da = dmp(cnf_loc)

        params_requried = ['user_id', 'file_id']
        d = json.loads(request.data)
        if d['file_id']:
            file_id = da.remove_file(d['file_id'])
        else:
            return self.usage('MissingMetaDataParameters', 400, params_required, {})
        return file_id

class Tracks(Resource):
    """
    Class to handle the http requests for retrieving the list of files for a
    given user handle
    """
    
    def get(self):
        cnf_loc=os.path.dirname(os.path.abspath(__file__)) + '/mongodb.cnf'
        da = dmp(cnf_loc)
        
        # TODO Placeholder code
        user_id = request.args.get('user_id')
        
        params = [user_id]

        # Display the parameters available
        if sum([x is None for x in params]) == len(params):
            return self.usage(None, 200)
        
        # ERROR - one of the required parameters is NoneType
        if sum([x is not None for x in params]) != len(params):
            return self.usage('MissingParameters', 400, {'user_id' : user_id})
        
        files = da.get_files_by_user(user_id, rest=True)
        
        return {
            '_links': {
                '_self': request.base_url,
                '_parent' : request.url_root + 'mug/api/dmp'
            },
            'files': files
        }


class TrackHistory(Resource):
    """
    Class to handle the http requests for retrieving the list of file history of
    a given file for a given user handle
    """
    
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
                '_self': request.base_url,
                '_parent' : request.url_root + 'mug/api/dmp'
            },
            'history_files': files
        }

class ping(Resource):
    """
    Class to handle the http requests to ping a service
    """
    
    def get(self):
        from . import release
        res = {
            "status":  "ready",
            "version": release.__version__,
            "author":  release.__author__,
            "license": release.__license__,
            "name":    release.__rest_name__,
            "description": release.__description__,
            "_links" : {
                '_self' : request.base_url,
                '_parent' : request.url_root + 'mug/api/dmp'
            }
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
api.add_resource(EndPoints, "/mug/api/dmp", endpoint='dmp_root')

#   Get the data for a specific track
api.add_resource(Track, "/mug/api/dmp/track", endpoint='track')

#   List the available species for which there are datasets available
api.add_resource(Tracks, "/mug/api/dmp/tracks", endpoint='tracks')

#   List file history
api.add_resource(TrackHistory, "/mug/api/dmp/trackHistory", endpoint='trackHistory')

#   Service ping
api.add_resource(ping, "/mug/api/dmp/ping", endpoint='dmp-ping')


"""
Initialise the server
"""
if __name__ == "__main__":
    app.run(port=5001, debug=True, use_reloader=False)
