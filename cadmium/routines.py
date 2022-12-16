from pygcode import *
import numpy as np

def GoAboveRoutine(X,Y,safe_z):
    yield GCodeRapidMove(Z=safe_z)
    yield GCodeRapidMove(X=X,Y=Y)
def DirectDrillRoutine(down_z,safe_z):
    # TODO assert that spindle is running
    yield GCodeLinearMove(Z=down_z)
    yield GCodeLinearMove(Z=safe_z)
    
def OnionBoring(zs,o,r,step_over,step_down,tr):
    ox,oy = o
    z_up,z_down = zs
    assert step_over <= tr
    def gen(safe_z):
        yield GCodeRapidMove(Z=safe_z)
        yield GCodeRapidMove(X=ox,Y=oy)
        for z in np.arange(z_up,z_down,-step_down):
            for i in np.arange(step_over,r,step_over):
                yield GCodeLinearMove(Z=z)
                yield GCodeLinearMove(X=ox-i)
                yield GCodeArcMoveCW(I=i,X=ox-i,Y=oy,Z=z)
                yield GCodeLinearMove(X=ox-r+tr)
                yield GCodeArcMoveCW(I=r-tr,X=ox-r,Y=oy,Z=z)
        yield GCodeRapidMove(Z=safe_z,X=ox,Y=oy)
    return gen