from cadmium.cadmium import *
from cadmium.compiler import *
from sdf import *
from pygcode import *

from cadmium.linearize import LinearizePostProcessor
from cadmium.routines import OnionBoring

tool_radius = 1.6
tool = Tool(shape=capped_cylinder(ORIGIN,Z*5,tool_radius)) #3.2mm flat 2 flutes endmill,center cutting
feed = 150
speed = 1000

fw,fl,fh = (80,80,10)
sw,sl,sh = (340,95,10)

inset = tool_radius
stock=box((sw,sl,sh)).translate((-340/2,-95/2,-31/2)) # box with corner at zero
stock = stock.translate((fw,0,0)) # put the shape under
stock -= box((fw,fl,fh)).translate((fw/2,-fl/2,-fh/2)).translate((-inset,-inset,0)) # inset the shape
stock |= sphere(tool_radius) # draw ORIGIN

def clear_perimeter(Z,a,b):
    xa,ya=a
    xb,yb=b
    def gen(safe_z):
        yield GCodeRapidMove(Z=safe_z)
        yield GCodeRapidMove(X=xa,Y=ya)
        yield GCodeLinearMove(Z=Z)
        yield GCodeLinearMove(Y=yb)
        yield GCodeLinearMove(X=xb)
        yield GCodeLinearMove(Y=ya)
        yield GCodeLinearMove(X=xa)
        yield GCodeRapidMove(Z=safe_z)
    return gen  

def clear_rect(a,b,step_over,step_down):
    xa,ya,za=a
    xb,yb,zb=b
    def gen(safe_z):
        yield GCodeRapidMove(Z=safe_z)
        yield GCodeRapidMove(X=xa,Y=ya)
        for i,z in enumerate([ *np.arange(za,zb,-step_down), zb]):
            yield GCodeLinearMove(Z=z)
            if i%2==0:
                for x in np.arange(xa,xb,step_over*2):
                    yield GCodeLinearMove(X=x)
                    yield GCodeLinearMove(Y=yb)
                    yield GCodeLinearMove(X=x+step_over)
                    yield GCodeLinearMove(Y=ya)
            else :
                for y in np.arange(ya,yb,step_over*2):
                    yield GCodeLinearMove(Y=y)
                    yield GCodeLinearMove(X=xb)
                    yield GCodeLinearMove(Y=y+step_over)
                    yield GCodeLinearMove(x=xa)
            if i==0:
                yield GCodeStopSpindle()
                yield GCodePauseProgram()
                yield GCodeStartSpindleCW()
        yield GCodeRapidMove(Z=safe_z)# TODO rapid move to the center of the rect too
        
    return gen


# def clear_top():
p_origin = (0,0)
p_o_corner = (tool_radius,tool_radius)
p_corner = (fw+tool_radius,fl+tool_radius)
p_tr = (fw+tool_radius*2,fl+tool_radius*2)

ext_holes = [ (10+X*20,10+Y*20) for (X,Y) in [(1,0),(2,0),(3,1),(3,3),(2,3),(1,3),(0,3),(0,1)] ]
ext_holes = [ (-X,Y) for X,Y in ext_holes]
nema_holes = [(40+23.57*X,34+23.57*Y) for (X,Y) in [(-1,-1),(-1,1),(1,1),(1,-1)]]
nema_holes = [ (-X,Y) for X,Y in nema_holes]

step_down=.5

program = Program(
    [
        Operation(tool=tool,path=lambda safe_z : [
            GCodeRapidMove(Z=safe_z),
            GCodeRapidMove(X=0,Y=0),
            GCodeSpindleSpeed(speed),
            GCodeStartSpindleCW(),
            GCodeFeedRate(feed),
        ]),

        # Operation(tool=tool,path=clear_rect(
        # a=(-tool_radius,-tool_radius,0),
        # b=(fw+tool_radius,fl+tool_radius,fh-sh),
        # step_over=tool_radius*1.9,
        # step_down=.5)),
        # remove the top

        # *(Operation(tool=tool,path=clear_perimeter(z,(-tool_radius,-tool_radius),(fw+tool_radius,fl+tool_radius)))
        # for i,z in enumerate(np.arange(fh-sh,-sh,-step_down))), #perimeter

        *(Operation(tool=tool,path=OnionBoring(
            zs=(fh-sh,-sh),
            o=(x,y),
            r=2.5,
            step_over=tool_radius*.8,
            step_down=step_down,
            tr=tool_radius
        )) for x,y in [*ext_holes,*nema_holes]), # M5 bores

        *(Operation(tool=tool,path=OnionBoring(
            zs=(fh-sh,6.5-sh),
            o=(x,y),
            r=5.0,
            step_over=tool_radius*.8,
            step_down=step_down,
            tr=tool_radius
        )) for x,y in ext_holes), # M5 counter bores

        *(Operation(tool=tool,path=OnionBoring(
            zs=(fh-sh,-sh), # TODO should be about 10.5
            o=(x,y),
            r=6.3/2,
            step_over=tool_radius*.8,
            step_down=step_down,
            tr=tool_radius
        )) for x,y in nema_holes), # M5 insert bores

        Operation(tool=tool,path=OnionBoring(
            zs=(fh-sh,-sh),
            o=(tool_radius-40,tool_radius+34),
            r=7.5,
            step_over=tool_radius*.8,
            step_down=step_down,
            tr=tool_radius
        )), # Nema23 shaft opening

        Operation(tool=tool,path=lambda _ : [GCodeStopSpindle(),GCodeEndProgram()]),
    ]
)
run = Run(
    stock=stock,
    program=program,
    machine=Machine()
)


with open("plate.gcode",mode="w") as f:
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