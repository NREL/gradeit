"""
GradeIT
The Grade Inference Tool
=======================

Provides an interface for accessing road grade and elevation data given a
sequence of coordinates.

Available modules
-----------------
grade
    For retrieving road grade values given coordinates

elevation
    For retrieving elevation values given coordinates

gradeit
    Combines the functionality of elevation and grade modules
"""

from .gradeit import gradeit
