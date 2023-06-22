from typing import List

from pydantic import BaseModel


class CutCoordParam(BaseModel):
    coronal: List[float] = []
    sagittal: List[float] = []
    horizontal: List[float] = []


class StatImageParam(BaseModel):
    threshold: List[float] = [0.0, 0.0]
    cut_coords: CutCoordParam = CutCoordParam()
