from cadmium.cadmium import *
from cadmium.compiler import *
from sdf import *
from pygcode import *

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

# validated (POM, from top surface, so depth is not 100% accurate)
# s1000 f300 d.5 => 150 units removed/s
# s1000 f200 d.75 => 150 units removed/s
# s1000 f250 d1 => 250 units removed/s (did not like it)
# s1000 f200 d1 => 200 units removed/s (did not like it)
# s1000 f500 d.5 => 250 units removed/s
# s1000 f500 d.75 => 375 units removed/s (on the limit of what I'd run)
# s1000 f600 d.5 => 300 units removed/s
# s1000 f700 d.5 => 350 units removed/s

speed=1000
feed=600
depth=.5

program = Program(
    [
        Operation(tool=tool,path=lambda safe_z : [
            GCodeRapidMove(Z=safe_z),
            GCodeRapidMove(X=0,Y=0),
            GCodeSpindleSpeed(speed),
            GCodeStartSpindleCW(),
            GCodeFeedRate(feed),
        ]),

        Operation(tool=tool,path=lambda safe_z : [
            GCodeLinearMove(Z=-depth),
            GCodeLinearMove(Y=33),
            GCodeLinearMove(Z=safe_z),
        ]),

        Operation(tool=tool,path=lambda _ : [GCodeStopSpindle(),GCodeEndProgram()]),
    ]
)
run = Run(
    stock=stock,
    program=program,
    machine=Machine()
)


with open("linear.gcode",mode="w") as f:
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