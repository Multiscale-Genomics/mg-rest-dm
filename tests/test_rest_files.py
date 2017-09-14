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

def _run_tests(details):
    """
    """
    assert 'files' in details
    assert len(details['files']) is not 0

    for file_meta in details['files']:
        print(file_meta)
        assert 'file_path' not in file_meta

def test_tracks_01(client):
    """
    Test that specifying a user_id returns information
    """
    rest_value = client.get(
        '/mug/api/dmp/files',
        headers=dict(Authorization='Authorization: Bearer teststring')
    )
    details = json.loads(rest_value.data)
    _run_tests(details)

# users = ["adam", "ben", "chris", "denis", "eric", "test"]
# def test_tracks_01(client):
#     """
#     Test that specifying a user_id returns information
#     """
#     rest_value = client.get('/mug/api/dmp/tracks?user_id=adam')
#     details = json.loads(rest_value.data)
#     _run_tests(details)

# def test_tracks_02(client):
#     """
#     Test that specifying a user_id returns information
#     """
#     rest_value = client.get('/mug/api/dmp/tracks?user_id=ben')
#     details = json.loads(rest_value.data)
#     _run_tests(details)

# def test_tracks_03(client):
#     """
#     Test that specifying a user_id returns information
#     """
#     rest_value = client.get('/mug/api/dmp/tracks?user_id=chris')
#     details = json.loads(rest_value.data)
#     _run_tests(details)

# def test_tracks_04(client):
#     """
#     Test that specifying a user_id returns information
#     """
#     rest_value = client.get('/mug/api/dmp/tracks?user_id=denis')
#     details = json.loads(rest_value.data)
#     _run_tests(details)

# def test_tracks_05(client):
#     """
#     Test that specifying a user_id returns information
#     """
#     rest_value = client.get('/mug/api/dmp/tracks?user_id=eric')
#     details = json.loads(rest_value.data)
#     _run_tests(details)