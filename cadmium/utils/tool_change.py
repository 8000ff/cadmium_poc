from pygcode import *

# def ChangeUsingPause(park=True,park_position=(0,0,1),return_position=None,safe_z=1):
#     yield GCodeStopSpindle()
#     yield GCodeRapidMove(Z=safe_z)
#     if park:
#         x,y,z = park_position
#         yield GCodeRapidMove(X=x,Y=y,Z=z)
#     yield GCodePauseProgram()
#     if return_position:
#         x,y,z = return_position
#         yield GCodeRapidMove(X=x,Y=y,Z=z)
#     yield 