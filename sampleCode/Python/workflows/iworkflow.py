from abc import ABC, abstractmethod

class IWorkflow(ABC):
    @staticmethod
    @abstractmethod
    def examples(bearer_token):
        pass
