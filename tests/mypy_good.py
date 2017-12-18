from annotypes import Array
from annotypes.py2_examples.simple import Simple
from annotypes.py2_examples.manyargs import ManyArgs
from annotypes.py2_examples.composition import CompositionClass
from annotypes.py2_examples.enumtaker import EnumTaker, Status
from annotypes.py2_examples.table import LayoutTable, Manager

a = Simple(32)
b = Simple(45, "")
c = ManyArgs(Array(["x"]), [0], 1, 10, "mm")
d = CompositionClass(2.0, "/tmp")
e = EnumTaker(Status.bad)
layout = LayoutTable(Array[str](["BLOCK"]),
                     Array[str](["MRI"]),
                     Array[float]([0.5]),
                     Array[float]([2.5]),
                     Array[bool]([True]))
Manager().set_layout(layout)
