# MIT License

# Copyright (c) 2023 IMPLAN

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import uuid
class Event:
    def __init__(self, title, id_=None, project_id=None, tags=None):
        self.title = title
        self.id = id_ if id_ is not None else str(uuid.uuid4())
        self.project_id = project_id
        self.tags = tags if tags is not None else []
        self._impact_event_type = "Empty"

    @property
    def impact_event_type(self):
        return self._impact_event_type

    @impact_event_type.setter
    def impact_event_type(self, value):
        self._impact_event_type = value

    def to_dict(self):
        return {
            "impactEventType": self.impact_event_type,
            "title": self.title,
            "id": self.id,
            "projectId": self.project_id,
            "tags": self.tags
        }
