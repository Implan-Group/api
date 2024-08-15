import uuid
class Event:
    def __init__(self, title, id=None, project_id=None, tags=None):
        self.title = title
        self.id = id if id is not None else str(uuid.uuid4())
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