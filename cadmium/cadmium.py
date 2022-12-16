from dataclasses import dataclass, field
from typing import Callable, Iterator, List,Union
from pygcode import GCode,Machine
from sdf import SDF3

@dataclass
class Tool:
    # TODO study 2D to 3D sdf
    # Describes the shape of the tool using a signed distance function
    shape : SDF3
    # Takes an angle in the interval [0,pi] and return a proptional engagement feed [0,1]
    engage : Callable[[float], float] = lambda x : 1
@dataclass
class Stock:
    # TODO add material description
    shape : SDF3
@dataclass
class Operation:
    tool : Tool
    path : Callable[[float],Iterator[GCode]]
    setup : Callable[[SDF3],SDF3] = lambda shape : shape
    workholding : Union[SDF3,None] = None
@dataclass
class Program:
    # TODO add the following policies: safe_height, tool_change, spin, optimizers
    operations : List[Operation]
@dataclass
class Run:
    stock : Stock
    machine : Machine
    program : Program