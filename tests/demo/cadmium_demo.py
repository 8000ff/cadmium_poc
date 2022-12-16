from sdf import *
from pygcode import *
from itertools import chain

from cadmium.cadmium import Operation, Program, Tool,Run,Stock
from cadmium.compiler import GCodeCompiler,CompilerParams
from cadmium.routines import *
from cadmium.linearize import LinearizePostProcessor

stock = Stock(box((80,80,10)).translate((0,0,-5)))
machine = Machine()
tool_drill = Tool(capped_cone((0,0,0),(0,0,3),0,5),0)
tool_endmill = Tool(capped_cylinder((0,0,0),(0,0,3),3),1)

# This is a placeholder circular ramping routine, mostly to demo the G2/G3 arc linearization
# WARNING don't use this routine, it will 100% destroy your tool
def BoreRoutine(X,Y,bore_diameter,tool_diameter,down_z,safe_z):
    arc_offset = bore_diameter/2 - tool_diameter/2
    yield GCodeRapidMove(Z=safe_z)
    yield GCodeStartSpindleCW()
    yield GCodeRapidMove(X=X-arc_offset,Y=Y)
    yield GCodeArcMoveCW(X=X-arc_offset,Y=Y,Z=down_z,I=+arc_offset)
    yield GCodeArcMoveCW(X=X-arc_offset,Y=Y,Z=down_z,I=+arc_offset)
    yield GCodeLinearMove(X=X,Y=Y,Z=safe_z)

ext_holes = [ (10+X*20,10+Y*20) for (X,Y) in [(1,0),(2,0),(3,1),(3,3),(2,3),(1,3),(0,3),(0,1)] ]
nema_holes = [(40+23.57*X,34+23.57*Y) for (X,Y) in [(-1,-1),(-1,1),(1,1),(1,-1)]]

def nema_drilling_path(safe_z):
    for (X,Y) in nema_holes:
        yield from GoAboveRoutine(X,Y,safe_z)
        yield from DirectDrillRoutine(down_z=-10,safe_z=safe_z)

def ext_drilling_path(safe_z):
    for (X,Y) in ext_holes:
        yield from GoAboveRoutine(X,Y,safe_z)
        yield from DirectDrillRoutine(down_z=-10,safe_z=safe_z)

def ext_counter_bore_path(safe_z):
    for (X,Y) in ext_holes:
        yield from GoAboveRoutine(X,Y,safe_z)
        yield from BoreRoutine(X,Y,10,5,-3,1)

nema_drilling = Operation(tool_drill,nema_drilling_path)
ext_drilling = Operation(tool_drill,ext_drilling_path)
ext_counter_bore = Operation(tool_endmill,ext_counter_bore_path)
rod_bore = Operation(tool_endmill,lambda safe_z : chain(GoAboveRoutine(40,34,safe_z),BoreRoutine(40,34,15,5,-10,safe_z)))

run = Run(stock=stock,machine=machine,program=Program([nema_drilling,ext_drilling,ext_counter_bore,rod_bore]))



with open("demo.gcode",mode="w") as f:
    lines = LinearizePostProcessor(
        GCodeCompiler(
            CompilerParams(
                run=run,
                tool_change_procedure= lambda a,b : [ GCodeStopSpindle(), GCodePauseProgram(), GCodeStartSpindleCW() ],
            )
        )
    )

    f.writelines([ str(line)+'\n' for line in lines])