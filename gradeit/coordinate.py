from __future__ import annotations
from dataclasses import dataclass

from shapely.geometry import Point


@dataclass
class Coordinate:
    geometry: Point

    @classmethod
    def from_lat_lon(cls, latitude: float, longitude: float) -> Coordinate:
        """
        Create a Coordinate from a latitude and longitude
        """
        return Coordinate(geometry=Point(longitude, latitude))

    @property
    def latitude(self) -> float:
        """
        Return the latitude of the Coordinate
        """
        return self.geometry.y

    @property
    def longitude(self) -> float:
        """
        Return the longitude of the Coordinate
        """
        return self.geometry.x
