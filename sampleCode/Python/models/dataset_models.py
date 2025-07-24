class Dataset:
    """
    The Model for a Dataset
    """
    def __init__(self,
                 id: int,
                 description: str,
                 is_default: bool):
        self.id = id
        self.description = description
        self.is_default = is_default