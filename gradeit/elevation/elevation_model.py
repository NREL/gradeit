from abc import ABCMeta, abstractmethod
from typing import List


from gradeit.coordinate import Coordinate


class ElevationModel(metaclass=ABCMeta):
    """
    Abstract class for elevation lookup models
    """

    @abstractmethod
    def get_elevation(self, trace: List[Coordinate]) -> List[float]:
        """
        Get elevation (in feet) for a list of points in a trace
        """
        pass
