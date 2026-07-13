from enum import Enum


class ModelBuildStatus(Enum):
    NOTBUILT = 1
    NEW = 2
    BUILT = 3
    COMPLETE = 4
    ERROR = 5