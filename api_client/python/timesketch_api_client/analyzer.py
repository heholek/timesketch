# Copyright 2020 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Timesketch API analyzer result object."""
from __future__ import unicode_literals

import datetime
import json

from . import definitions
from . import resource


class AnalyzerResult(resource.BaseResource):
    """Class to store and retrieve session information for an analyzer."""

    def __init__(self, timeline_id, session_id, sketch_id, api):
        """Initialize the class."""
        self._session_id = session_id
        self._sketch_id = sketch_id
        self._timeline_id = timeline_id
        resource_uri = (
            '{0:s}/sketches/{1:d}/timelines/{2:d}/analysis/').format(
                api.api_root, sketch_id, timeline_id)
        super(AnalyzerResult, self).__init__(api, resource_uri)

    def _fetch_data(self):
        """Returns..."""
        response = self.api.session.get(self.resource_uri)
        if not response.status_code in definitions.HTTP_STATUS_CODE_20X:
            return {}

        data = response.json()

        objects = data.get('objects')
        if not objects:
            return {}

        for result in objects[0]:
            result_id = result.get('analysissession_id')
            if result_id != self._session_id:
                continue
            status_list = result.get('status', [])
            if len(status_list) != 1:
                return {}
            status = status_list[0]

            timeline = result.get('timeline', {})

            return {
                'id': result_id,
                'analyzer': result.get('analyzer_name', 'N/A'),
                'results': result.get('result'),
                'description': result.get('description', 'N/A'),
                'user': result.get('user', {}).get('username', 'System'),
                'parameters': json.loads(result.get('parameters', '{}')),
                'status': status.get('status', 'Unknown'),
                'status_date': status.get('updated_at', ''),
                'log': result.get('log', ''),
                'created': result.get('created_at'),
                'timeline': timeline.get('name', 'N/A'),
                'timeline_id': timeline.get('id', -1),
                'timeline_user': timeline.get('user', {}).get(
                    'username', 'System'),
                'timeline_name': timeline.get('name', 'N/A'),
                'timeline_deleted': timeline.get('deleted', False),
            }

        return {}

    @property
    def id(self):
        """Returns the session ID."""
        return self._session_id

    @property
    def log(self):
        """Returns back logs from the analyzer session, if there are any."""
        data = self._fetch_data()
        return data.get('log', 'No recorded logs.')

    @property
    def results(self):
        """Returns the results from the analyzer session."""
        data = self._fetch_data()
        return data.get('results', 'No results yet.')

    @property
    def status(self):
        """Returns the current status of the analyzer run."""
        data = self._fetch_data()
        return data.get('status', 'Unknown')

    @property
    def status_string(self):
        """Returns a longer version of a status string."""
        data = self._fetch_data()
        return '[{0:s}] Status: {1:s}'.format(
            data.get('status_date', datetime.datetime.utcnow().isoformat()),
            data.get('status', 'Unknown')
        )
