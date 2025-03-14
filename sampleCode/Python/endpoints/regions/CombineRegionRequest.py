class CombineRegionRequest:
    def __init__(self, description, hashids, urids=None):
        self.description = description
        self.hashids = hashids
        self.urids = urids if urids is not None else []

    def to_dict(self):
        return {
            "description": self.description,
            "hashIds": self.hashids,
            "urids": self.urids
        }
