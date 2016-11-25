"""
Copyright 2016 EMBL-European Bioinformatics Institute

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

app = Flask(__name__)
api = Api(app)


class GetTracks(Resource):
    """
    Class to handle the http requests for retrieving the list of files for a
    given user handle
    """
    
    def get(self):
        da = dmp()
        
        # TODO Placeholder code
        user_id = request.args.get('user_id')
        files = da.get_files_by_user(user_id, rest=True)
        
        return {
            '_links': {
                'self': request.base_url,
            },
            'files': files
        }

# TODO
# For the services where there needs to be an extra layer (adjacency lists),
# then there needs to be a way of forwarding for this. But the majority of
# things can be redirected to the raw files for use as a track.
#

"""
Define the URIs and their matching methods
"""
#   List the available species for which there are datasets available
api.add_resource(GetTracks, "/rest/v0.0/getTracks", endpoint='tracks')

#   List the available assemblies for a given species with links
#api.add_resource(GetTrack, "/rest/v0.0/getTrack", endpoint='track')


"""
Initialise the server
"""
if __name__ == "__main__":
    app.run()
