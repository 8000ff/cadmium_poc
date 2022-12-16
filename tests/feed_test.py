from webbrowser import Opera
from cadmium.cadmium import *
from cadmium.compiler import *
from sdf import *
from pygcode import *
from itertools import chain

tool = Tool(shape=capped_cylinder(ORIGIN,Z*5,1.6)) #3.2mm flat 2 flutes endmill,center cutting

def clear_path(feed,speed,length,depth,offset=0):
    def gen(safe_z):
        yield GCodeRapidMove(Z=safe_z)
        yield GCodeRapidMove(X=offset,Y=0,Z=safe_z)
        yield GCodeSpindleSpeed(speed)
        yield GCodeStartSpindleCW()
        yield GCodeFeedRate(feed)
        yield GCodeLinearMove(X=offset,Y=0,Z=depth)
        yield GCodeLinearMove(X=offset,Y=length,Z=depth)
        yield GCodeRapidMove(Z=safe_z)
    return gen
        
program = Program(
    [
        *[Operation(tool=tool,path=clear_path(feed=75,speed=500,length=-25,offset=i,depth=-.5)) for i in range(25)],
        # Operation(tool=tool,path=clear_path(feed=25,speed=500,length=-25,offset=0,depth=-.5)),
        Operation(tool=tool,path=lambda _ : [GCodeStopSpindle(),GCodeEndProgram()])
    ]
)
run = Run(
    stock=box((80,80,40)).translate((0,0,-40)),
    program=program,
    machine=Machine()
)


with open("feed_test.gcode",mode="w") as f:
    lines = GCodeCompiler(
            CompilerParams(
                run=run,
                tool_change_procedure= lambda a,b : [],
            )
        )

    f.writelines([ str(line)+'\n' for line in lines])