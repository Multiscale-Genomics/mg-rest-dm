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

from __future__ import print_function

import os
import tempfile
import json
import pytest

from context import app

@pytest.fixture
def client(request):
    """
    Definges the client object to make requests against
    """
    db_fd, app.APP.config['DATABASE'] = tempfile.mkstemp()
    app.APP.config['TESTING'] = True
    client = app.APP.test_client()

    def teardown():
        """
        Close the client once testing has completed
        """
        os.close(db_fd)
        os.unlink(app.APP.config['DATABASE'])
    request.addfinalizer(teardown)

    return client

def test_endpoints(client):
    """
    Test that the root endpoint is returning the expected keys
    """
    rest_value = client.get('/mug/api/dmp')
    details = json.loads(rest_value.data)
    #print(details)
    assert '_links' in details

def test_ping(client):
    """
    Test that the ping function is returning the status key
    """
    rest_value = client.get('/mug/api/dmp/ping')
    details = json.loads(rest_value.data)
    #print(details)
    assert 'status' in details

def test_track(client):
    """
    Test that the track endpoint is returning the usage paramerts
    """
    rest_value = client.get('/mug/api/dmp/track')
    details = json.loads(rest_value.data)
    #print(details)
    assert 'usage' in details

def test_tracks(client):
    """
    Test that the tracks endpoint is returning the usage paramerts
    """
    rest_value = client.get('/mug/api/dmp/tracks')
    details = json.loads(rest_value.data)
    #print(details)
    assert 'usage' in details
    assert len(details['usage']['parameters']) is not 0

def test_tracks_01(client):
    """
    Test that specifying a user_id returns information
    """
    rest_value = client.get('/mug/api/dmp/tracks?user_id=adam')
    details = json.loads(rest_value.data)
    #print(details)
    assert 'files' in details

def test_tracks_02(client):
    """
    Test that when specifying one of the known test users then there are a list
    of returned files
    """
    rest_value = client.get('/mug/api/dmp/tracks?user_id=adam')
    details = json.loads(rest_value.data)
    #print(details)
    assert len(details['files']) is not 0

def test_trackhistory(client):
    """
    Test that the tracks endpoint is returning the usage paramerts
    """
    rest_value = client.get('/mug/api/dmp/trackHistory')
    details = json.loads(rest_value.data)
    print(details)
    assert 'usage' in details
