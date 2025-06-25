class CombineRegionRequest:
    """
    The Model for a Combine Region Request

    https://github.com/Implan-Group/api/blob/main/impact/readme.md#build-combined-region-post
    """

    def __init__(self,
                 description: str,
                 hash_ids: list[int] | None = None,
                 urids: list[int] | None = None):
        self.description = description
        self.hashIds = hash_ids if hash_ids is not None else []
        self.urids = urids if urids is not None else []