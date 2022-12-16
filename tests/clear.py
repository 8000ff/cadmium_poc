from cadmium.cadmium import *
from cadmium.compiler import *
from sdf import *
from pygcode import *
import numpy as np
from cadmium.linearize import LinearizePostProcessor
from cadmium.routines import OnionBoring

tool_radius = 1.6
tool = Tool(shape=capped_cylinder(ORIGIN,Z*5,tool_radius)) #3.2mm flat 2 flutes endmill,center cutting

fw,fl,fh = (80,80,10)
sw,sl,sh = (340,95,10)

inset = tool_radius
stock=box((sw,sl,sh)).translate((-340/2,-95/2,-31/2)) # box with corner at zero
stock = stock.translate((fw,0,0)) # put the shape under
stock -= box((fw,fl,fh)).translate((fw/2,-fl/2,-fh/2)).translate((-inset,-inset,0)) # inset the shape
stock |= sphere(tool_radius) # draw ORIGIN

# s1000 f600 d.5 => 300 units removed/s

speed=1000
feed=600
depth=.5

def clear(step=tool_radius*2):
    def gen(safe_z):
        for i,z in enumerate([ *np.arange(0,-10,-depth), -10]):
            yield GCodeLinearMove(Z=z)
            if i%2==0:
                for x in np.arange(0,-100,-step):
                    yield GCodeLinearMove(X=x)
                    yield GCodeLinearMove(Y=-100)
                    yield GCodeLinearMove(X=x+tool_radius)
                    yield GCodeLinearMove(Y=0)
            else :
                for y in np.arange(0,-100,-step):
                    yield GCodeLinearMove(Y=y)
                    yield GCodeLinearMove(X=-100)
                    yield GCodeLinearMove(Y=y-step)
                    yield GCodeLinearMove(x=0)
            if i==0:
                yield GCodeStopSpindle()
                yield GCodePauseProgram()
                yield GCodeStartSpindleCW()
    return gen

program = Program(
    [
        Operation(tool=tool,path=lambda safe_z : [
            GCodeRapidMove(Z=safe_z),
            GCodeRapidMove(X=0,Y=0),
            GCodeSpindleSpeed(speed),
            GCodeStartSpindleCW(),
            GCodeFeedRate(feed),
        ]),

        Operation(tool=tool,path=clear()),

        Operation(tool=tool,path=lambda _ : [GCodeStopSpindle(),GCodeEndProgram()]),
    ]
)
run = Run(
    stock=stock,
    program=program,
    machine=Machine()
)


with open("clear.gcode",mode="w") as f:
    lines = (
        LinearizePostProcessor(
            GCodeCompiler(
                CompilerParams(
                    run=run,
                    tool_change_procedure= lambda a,b : [],
                )
            )
            ,delta=.5)
    )
    f.writelines([ str(line)+'\n' for line in lines])