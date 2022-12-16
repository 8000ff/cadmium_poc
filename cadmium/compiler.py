from dataclasses import dataclass,field
from distutils.command.install_egg_info import safe_name
from typing import Callable,List, Union
from more_itertools import windowed
from pygcode import GCode,GCodeStartSpindleCW,GCodeStopSpindle,GCodeEndProgram

from cadmium.cadmium import Run
from cadmium.safe_height import ConstantSafeHeight

@dataclass
class CompilerParams:
    run : Run
    safe_height_policy = ConstantSafeHeight(5)
    # TODO add support for program split
    tool_change_procedure : Callable[[int,int],List[GCode]]
    # checks : field(default_factory=list) List[Callable[[Run], bool]]
    # post_operation_gcode : field(default_factory=list)
    # pre_operation_gcode : field(default_factory=lambda : [ GCodeStartSpindleCW ])
    # pre_gcode : field(default_factory=lambda : [ GCodeStartSpindleCW ])
    # post_gcode : field(default_factory= lambda : [ GCodeStopSpindle,GCodeEndProgram ])

def GCodeCompiler(params : CompilerParams) -> Union[List[GCode],str]:
    # checks_result = [ check(params.run) for check in params.checks ]
    # if not all(checks_result):
    #     return f"Some checks failed [${ [('v' if check else 'x') for check in checks_result] }]"
    tools = [ operation.tool for operation in params.run.program.operations ]
    tools_changes = [i for i, (a,b) in enumerate(windowed(tools,n=2)) if a != b]
    assert(len(tools_changes) == 0 or params.tool_change_procedure != None, 
    "As your operations use different tools, a tool change procedure is required.")
    def gen():
        # yield from params.pre_gcode
        operations = params.run.program.operations
        for i, operation in enumerate(operations):
            safe_height = params.safe_height_policy(operation)
            yield from operation.path(safe_height)
            if i in tools_changes:
                yield from params.tool_change_procedure(0,0) # TODO use tool numbering
            # if params.post_operation_gcode != None:
            #     yield from params.post_operation_gcode
        # yield from params.post_gcode
    return list(gen())