from typing import Union, List, Any

from annotypes import Anno, WithCallTypes

with Anno("The scannable axes, e.g. ['x', 'y'] or 'x'"):
    Axes = Union[List[str], str]

with Anno("The scannable units, e.g. ['mm', 'deg'] or 'mm'"):
    Units = Union[List[str], str]

with Anno("The first point to be generated, e.g. [0., 2.4] or 1."):
    Start = Union[List[float], float]

with Anno("The final point to be generated, e.g. [-8., 6.4] or 5."):
    Stop = Union[List[float], float]

with Anno("The number of points to generate, e.g. 5"):
    Size = int

with Anno("Whether to reverse on alternate runs"):
    Alternate = bool


def to_list(x: Any) -> List:
    if isinstance(x, list):
        return x
    else:
        return [x]


class Long(WithCallTypes):
    def __init__(self, axes: Axes, units: Units, start: Start, stop: Stop,
                 size: Size, alternate: Alternate = False):
        self.axes = to_list(axes)
        self.units = to_list(units)
        self.start = to_list(start)
        self.stop = to_list(stop)
        self.size = size
        self.alternate = alternate