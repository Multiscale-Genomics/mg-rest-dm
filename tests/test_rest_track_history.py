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


def test_track_history_01(client):
    """
    Test that specifying a user_id returns information
    """
    users = ["adam", "ben", "chris", "denis", "eric", "test"]

    for user in users:
        rest_value = client.get('/mug/api/dmp/tracks?user_id=' + user)
        results = json.loads(rest_value.data)
        #_run_tests(results)

        for result in results['files']:
            print(result['_id'])
            rest_value = client.get('/mug/api/dmp/trackHistory?user_id=' + user + '&file_id=' + result['_id'])
            history_results = json.loads(rest_value.data)
            print(history_results)

            assert 'history_files' in history_results
