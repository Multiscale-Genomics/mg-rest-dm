"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.

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

from __future__ import print_function

import json
import os
import logging

from flask import Flask, request, make_response
from flask_restful import Api, Resource

from dmp import dmp
from reader.bigbed import bigbed_reader
from reader.bigwig import bigwig_reader

from rest.mg_auth import authorized

APP = Flask(__name__)
logging.basicConfig()

def help_usage(error_message, status_code,
               parameters_required, parameters_provided):
    """
    Usage Help

    Description of the basic usage patterns for GET functions for the app,
    including any parameters that were provided byt he user along with the
    available parameters that are required/optional.

    Parameters
    ----------
    error_message : str | None
        Error message detailing what has gone wrong. If there are no errors then
        None should be passed.
    status_code : int
        HTTP status code.
    parameters_required : list
        List of the text names for each paramter required by the end point. An
        empty list should be provided if there are no parameters required
    parameters_provided : dict
        Dictionary of the parameters and the matching values provided by the
        user. An empyt dictionary should be passed if there were no parameters
        provided by the user.

    Returns
    -------
    str
        JSON formated status message to display to the user
    """
    parameters = {
        'user_id' : ['User ID', 'str', 'REQUIRED'],
        'file_id' : ['File ID', 'str', 'REQUIRED'],
        'chrom' : ['Chromosome', 'str', 'REQUIRED'],
        'start' : ['Start', 'int', 'REQUIRED'],
        'end' : ['End', 'int', 'REQUIRED'],
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

    if parameters_provided:
        message['provided_parameters'] = parameters_provided

    if error_message is not None:
        message['error'] = error_message

    return message

class EndPoints(Resource):
    """
    Class to handle the http requests for returning information about the end
    points
    """

    def get(self):
        """
        GET list all end points

        List of all of the end points for the current service.

        Example
        -------
        .. code-block:: none
           :linenos:

           curl -X GET http://localhost:5002/mug/api/dmp

        """
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

    @authorized
    def get(self, user_id):
        """
        GET  List values from the file

        Call to optain regions from the conpressed index files for Bed, Wig and
        TSV based file formats that contain genomic information

        Parameters
        ----------
        user_id : str
            User ID
        file_id : str
            Identifier of the file to retrieve data from
        chrom : str
            Chromosome identifier (1, 2, 3, chr1, chr2, chr3, I, II, III, etc)
            for the chromosome of interest
        start : int
            Start position for a selected region
        end : int
            End position for a selected region

        Returns
        -------
        file
            Returns a formated in the relevant file type with any genomic
            features matching the format of the file.

        Examples
        --------
        .. code-block:: none
           :linenos:

           curl -X GET http://localhost:5002/mug/api/dmp/track?user_id=test&file_id=test_file&chrom=1&start=1000&end=2000

        """
        file_id = request.args.get('file_id')
        chrom = request.args.get('chrom')
        start = request.args.get('start')
        end = request.args.get('end')

        params_requried = ['user_id', 'file_id', 'chrom', 'start', 'end']
        params = [user_id, file_id, chrom, start, end]

        # Display the parameters available
        if sum([x is None for x in params]) == len(params):
            return help_usage(None, 200, params_requried, {})

        # ERROR - one of the required parameters is NoneType
        if sum([x is not None for x in params]) != len(params):
            return help_usage('MissingParameters', 400, params_requried, {'user_id' : user_id})

        if user_id is not None:
            cnf_loc = os.path.dirname(os.path.abspath(__file__)) + '/mongodb.cnf'
            if os.path.isfile(cnf_loc) is True:
                dmp_api = dmp(cnf_loc)
            else:
                dmp_api = dmp(cnf_loc, test=True)

            file_obj = dmp_api.get_file_by_id(user_id, file_id)

            output_str = ''
            if file_obj['file_type'] in ['bed', 'bb']:
                bbr = bigbed_reader(file_obj['file_path'])
                output_str = bbr.get_range(chrom, start, end, 'bed')
            elif file_obj['file_type'] in ['wig', 'bw']:
                print(chrom, start, end, 'wig')
                bwr = bigwig_reader(file_obj['file_path'])
                output_str = bwr.get_range(chrom, start, end, 'wig')

            resp = make_response(output_str, 'application/tsv')
            resp.headers["Content-Type"] = "text"

            return resp

        return help_usage('Forbidden', 403, params_requried, {})

    @authorized
    def post(self, user_id):
        """
        POST Add a new file to the DM API

        Call to optain regions from the conpressed index files for Bed, Wig and
        TSV based file formats that contain genomic information

        Parameters
        ----------
        This should be passed as the data block with the HTTP request:

        json : dict
            user_id : str
                User identifier
            file_path : str
                Location of the file
            file_type : str
                Tag for the file extension. The valid parameters are defined
                within the DM API documentation (mg-dm-api)
            data_type : str
                What type of experiment is this data from. Options include
                    RNA-seq
                    ChIP-seq
                    MNase-seq
                    WGBS
                    HiC
            taxon_id : int
                Taxonomic identifier for a species (Human = 9606)
            compressed
                Options of the compression level of the file. If file is not
                compressed then do not include this parameter
            source_id : list
                List of file_ids that were used for generating this file
            meta_data : dict
                Hash array describing the relevant metadata for the file,
                including the assembly if relevant

        Returns
        -------
        file_id
            Returns the id of the stored file

        Example
        -------
        .. code-block:: none
           :linenos:

           curl -X POST -H "Content-Type: application/json" -d '{"user_id": "test_user", "data_type": "RNA-seq", "file_type": "fastq", "source_id": [], "meta_data": {"assembly" : "GCA_nnnnnnnn.nn"}, "taxon_id": 9606, "file_path": "/tmp/test/path/RNA-seq/testing_123.fastq"}' http://localhost:5002/mug/api/dmp/track

        """
        if user_id is not None:
            cnf_loc = os.path.dirname(os.path.abspath(__file__)) + '/mongodb.cnf'
            if os.path.isfile(cnf_loc) is True:
                dmp_api = dmp(cnf_loc)
            else:
                dmp_api = dmp(cnf_loc, test=True)

            new_track = json.loads(request.data)
            user_id = new_track['user_id'] if 'user_id' in new_track else None
            file_path = new_track['file_path'] if 'file_path' in new_track else None
            file_type = new_track['file_type'] if 'file_type' in new_track else None
            data_type = new_track['data_type'] if 'data_type' in new_track else None
            taxon_id = new_track['taxon_id'] if 'taxon_id' in new_track else None
            source_id = new_track['source_id'] if 'source_id' in new_track else None
            meta_data = new_track['meta_data'] if 'meta_data' in new_track else None
            compressed = new_track['compressed'] if 'compressed' in new_track else None

            params_required = ['user_id', 'file_path', 'file_type', 'data_type',
                               'taxon_id', 'source_id', 'meta_data']
            params = [user_id, file_path, file_type, data_type, taxon_id,
                      source_id, meta_data]

            # ERROR - one of the required parameters is NoneType
            if sum([x is not None for x in params]) != len(params):
                return help_usage('MissingParameters', 400, params_required,
                                  {'user_id' : user_id})

            new_track = json.loads(request.data)

            return dmp_api.set_file(
                user_id,
                file_path,
                file_type,
                data_type,
                taxon_id,
                compressed,
                source_id,
                meta_data
            )

        return help_usage('Forbidden', 403, [], {})

    @authorized
    def put(self, user_id):
        """
        PUT Update meta data

        Request to update the meta data for a given file. This allows for the
        adding or removal of key-value pairs from the meta data.

        Parameters
        ----------
        This should be passed as the data block with the HTTP request:

        json : dict
            user_id : str
                User identifier
            file_id : str
                ID of the stored file
            type : str
                Options are 'add_meta' or 'remove_meta' to modify they key-value
                pairs for the file entry. Minimum sets of pairs are defined
                within the DM API (mg-dm-api)
            meta_data : dict
                Hash array describing the relevant metadata key-value pairs that
                are to be added

        Returns
        -------
        file_id
            Returns the id of the stored file

        Example
        -------
        To add a new key value pair:

        .. code-block:: none
           :linenos:

           curl -X PUT -H "Content-Type: application/json" -d '{"type":"add_meta", "file_id":"<file_id>", "user_id":"test_user", "meta_data":{"citation":"PMID:1234567890"}}' http://localhost:5002/mug/api/dmp/track

        To remove a key value pair:

        .. code-block:: none
           :linenos:

           curl -X PUT -H "Content-Type: application/json" -d '{"type":"remove_meta", "file_id":"<file_id>", "user_id":"test_user", "meta_data":["citation"]}' http://localhost:5002/mug/api/dmp/track

        """
        if user_id is not None:
            cnf_loc = os.path.dirname(os.path.abspath(__file__)) + '/mongodb.cnf'
            if os.path.isfile(cnf_loc) is True:
                dmp_api = dmp(cnf_loc)
            else:
                dmp_api = dmp(cnf_loc, test=True)

            data_put = json.loads(request.data)
            file_id = data_put['file_id']

            params_required = ['user_id', 'file_id', 'type']

            if data_put['type'] == 'add_meta':
                for k in data_put['meta_data']:
                    result = dmp_api.add_file_metadata(
                        file_id, k, data_put['meta_data'][k])
            elif data_put['type'] == 'remove_meta':
                for k in data_put['meta_data']:
                    result = dmp_api.remove_file_metadata(file_id, k)
            else:
                return help_usage('MissingMetaDataParameters', 400, params_required,
                                  {'type' : ['add_meta', 'remove_meta']})
            return result

        return help_usage('Forbidden', 403, [], {})

    @authorized
    def delete(self, user_id):
        """
        DELETE Remove a file from the DM API

        Function to remove the file from teh DM API. This will result in the
        file being removed from the records and therefore not available within
        the VRE or from the RESTful interface

        Parameters
        ----------
        This should be passed as the data block with the HTTP request:
        json : dict
            user_id : str
                User identifier
            file_id : str
                ID of the stored file

        Example
        -------
        .. code-block:: none
           :linenos:

           curl -X DELETE -H "Content-Type: application/json" -d '{"file_id":"<file_id>", "user_id":"test_user"}' http://localhost:5002/mug/api/dmp/track

        """
        if user_id is not None:
            cnf_loc = os.path.dirname(os.path.abspath(__file__)) + '/mongodb.cnf'
            if os.path.isfile(cnf_loc) is True:
                dmp_api = dmp(cnf_loc)
            else:
                dmp_api = dmp(cnf_loc, test=True)

            params_required = ['user_id', 'file_id']
            data_delete = json.loads(request.data)
            if data_delete['file_id']:
                file_id = dmp_api.remove_file(data_delete['file_id'])
            else:
                return help_usage('MissingMetaDataParameters', 400, params_required,
                                  {})
            return file_id

        return help_usage('Forbidden', 403, [], {})

class Tracks(Resource):
    """
    Class to handle the http requests for retrieving the list of files for a
    given user handle
    """

    @authorized
    def get(self, user_id):
        """
        GET List user tracks

        Function to list the tracks that are owned by a single user.

        Parameters
        ----------



        Example
        -------
        .. code-block:: none
           :linenos:

           curl -X GET http://localhost:5002/mug/api/dmp/getTracks?user_id=<user_id>

        """
        if user_id is not None:
            cnf_loc = os.path.dirname(os.path.abspath(__file__)) + '/mongodb.cnf'

            print("USER ID:", user_id)
            if os.path.isfile(cnf_loc) is True:
                print("LIVE DM API")
                dmp_api = dmp(cnf_loc)
            else:
                print("TEST DM API")
                dmp_api = dmp(cnf_loc, test=True)

            params_required = ['user_id']
            params = [user_id]

            # Display the parameters available
            if sum([x is None for x in params]) == len(params):
                return help_usage(None, 200, params_required, {})

            # ERROR - one of the required parameters is NoneType
            if sum([x is not None for x in params]) != len(params):
                return help_usage('MissingParameters', 400, params_required, {'user_id' : user_id})

            files = dmp_api.get_files_by_user(user_id, rest=True)

            return {
                '_links': {
                    '_self': request.base_url,
                    '_parent' : request.url_root + 'mug/api/dmp'
                },
                'files': files
            }

        return help_usage('Forbidden', 403, [], {})


class TrackHistory(Resource):
    """
    Class to handle the http requests for retrieving the list of file history of
    a given file for a given user handle
    """

    @authorized
    def get(self, user_id):
        """
        GET the list of files that were used for generating the defined file

        Example
        -------
        .. code-block:: none
           :linenos:

           curl -X GET http://localhost:5002/mug/api/dmp/trackHistory?user_id=<user_id>&file_id=<file_id>
        """
        if user_id is not None:
            cnf_loc = os.path.dirname(os.path.abspath(__file__)) + '/mongodb.cnf'
            if os.path.isfile(cnf_loc) is True:
                dmp_api = dmp(cnf_loc)
            else:
                dmp_api = dmp(cnf_loc, test=True)

            file_id = request.args.get('file_id')

            params = [user_id, file_id]

            # Display the parameters available
            if sum([x is None for x in params]) == len(params):
                return help_usage(None, 200, [], {})

            # ERROR - one of the required parameters is NoneType
            if sum([x is not None for x in params]) != len(params):
                return help_usage('MissingParameters', 400, [],
                                  {
                                      'user_id' : user_id,
                                      'file_id' : file_id
                                  })

            files = dmp_api.get_file_history(user_id, file_id)

            return {
                '_links': {
                    '_self': request.base_url,
                    '_parent' : request.url_root + 'mug/api/dmp'
                },
                'history_files': files
            }

        return help_usage('Forbidden', 403, [], {})

class Ping(Resource):
    """
    Class to handle the http requests to ping a service
    """

    def get(self):
        """
        GET Status

        List the current status of the service along with the relevant
        information about the version.

        Example
        -------
        .. code-block:: none
           :linenos:

           curl -X GET http://localhost:5002/mug/api/dmp/ping

        """
        import rest.release as release
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


# Define the URIs and their matching methods
REST_API = Api(APP)

#   List the available end points for this service
REST_API.add_resource(EndPoints, "/mug/api/dmp", endpoint='dmp_root')

#   Get the data for a specific track
REST_API.add_resource(Track, "/mug/api/dmp/track", endpoint='track')

#   List the available species for which there are datasets available
REST_API.add_resource(Tracks, "/mug/api/dmp/tracks", endpoint='tracks')

#   List file history
REST_API.add_resource(TrackHistory, "/mug/api/dmp/trackHistory", endpoint='trackHistory')

#   Service ping
REST_API.add_resource(Ping, "/mug/api/dmp/ping", endpoint='dmp-ping')


# Initialise the server
if __name__ == "__main__":
    APP.run(port=5002, debug=True, use_reloader=False)
