class CombineRegionRequest:
    def __init__(self, description, hashIds, urids=None):
        self.description = description
        self.hash_ids = hashIds
        self.urids = urids if urids is not None else []

    def to_dict(self):
        return {
            "description": self.description,
            "hashIds": self.hash_ids,
            "urids": self.urids
        }