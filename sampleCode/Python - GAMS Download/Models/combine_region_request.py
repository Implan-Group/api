# noinspection PyPep8Naming

class CombineRegionRequest:
    """
    The Model for a Combine Region Request

    https://github.com/Implan-Group/api/blob/main/impact/readme.md#build-combined-region-post
    """

    def __init__(self, description: str, hashIds: list[int] | None = None, urids: list[int] | None = None):
        self.description = description
        self.hashIds = hashIds if hashIds is not None else []
        self.urids = urids if urids is not None else []