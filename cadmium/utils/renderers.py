# from platform import machine
# from pygcode import GCodeArcMove,transform,Machine
# from copy import copy
# from cadmium.model import Run
# from cadmium.linearize import linearize_arc

# def openscad(run : Run):
#     simulation = copy(run.machine)
#     segments = [] # list of segments and tool used
#     for operation in run.program.operations:
#         for c in operation.path:
#             if isinstance(c,GCodeArcMove):
#                 for sub in transform.linearize_arc(c,simulation.abs_pos,method_class=transform.ArcLinearizeMid):
#                     start = simulation.abs_pos
#                     simulation.process_gcodes(sub)
#                     stop = simulation.abs_pos
#                     segments.append((start,stop,operation.tool))
#             else:
#                 start = simulation.abs_pos
#                 simulation.process_gcodes(c)
#                 stop = simulation.abs_pos
#                 segments.append((start,stop,operation.tool))
#     return segments


# TODO parametric linearization
# def codes_points(run : Run,linearize_arcs : bool = True):
#     simulation = Machine()
#     gcodes = [] # unoptimised list of gcodes
#     steps = [simulation.abs_pos] # unoptimised list of points
#     for operation in run.program.operations:
#         for c in operation.path:
#             # print()
#             # print(c)
#             if linearize_arcs and isinstance(c,GCodeArcMove):
#                 # continue
#                 # for sub in transform.linearize_arc(c,simulation.abs_pos,method_class=transform.ArcLinearizeMid):
#                 for sub in linearize_arc(c,simulation.abs_pos):
#                     gcodes.append(sub)
#                     simulation.process_gcodes(sub)
#                     steps.append(simulation.abs_pos)
#             else:
#                 gcodes.append(c)
#                 simulation.process_gcodes(c)
#                 steps.append(simulation.abs_pos)
#     return gcodes,steps

# 
# def mpl_renderer(run : Run,bounds=None):
#     import matplotlib as mpl
#     from mpl_toolkits.mplot3d import Axes3D
#     import numpy as np
#     import matplotlib.pyplot as plt

#     mpl.rcParams['legend.fontsize'] = 10

#     fig = plt.figure()
#     axes = fig.gca(projection='3d')
    
#     if bounds != None:
#         a,b = bounds
#         ax,ay,az = a
#         bx,by,bz = b
#         axes.set_xlim3d(ax, bx)
#         axes.set_ylim3d(ay, by)
#         axes.set_zlim3d(bz, az) # don't ask
#     # m_pos_to_np = lambda pos : pos.vector.x+pos.vector.y*Y+pos.vector.z*Z

#     gcodes,steps = codes_points(run)
#     x,y,z = np.array([ step.vector for step in steps]).swapaxes(0,1)

#     # print(steps)

#     axes.plot(x, y, z, label='parametric curve')
#     axes.legend()

#     plt.show()