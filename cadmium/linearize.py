from typing import List
from pygcode import Position,GCode,GCodeArcMove,GCodeArcMoveCCW,GCodeArcMoveCW,GCodeLinearMove,Machine
import numpy as np
from numpy.linalg import norm
from collections import defaultdict

# Transforms a G2 or G3 move into a series of G1 moves
# The starting position is required as G2/G3 move assume the start of the arc is the current position
# delta is the distance between sampled points

def linearize_arc(code : GCodeArcMove, start : Position, delta : float = 1):
    assert isinstance(code,GCodeArcMoveCW) or isinstance(code,GCodeArcMoveCCW)
    cw_sign = -1 if isinstance(code,GCodeArcMoveCW) else 1
    # Built params from partial dict
    params = defaultdict(float,code.get_param_dict())
    turns = params['P'] or 1
    origin = np.array(start.vector)[np.newaxis,:]
    offset = np.array([params[p] for p in 'IJK'])[np.newaxis,:]
    target = np.array([params[p] for p in 'XYZ'])[np.newaxis,:]

    o_origin = - offset
    o_target = target - (origin + offset)
    assert norm(o_origin)
    assert norm(o_target)

    n_o_origin = o_origin[:,:2] / norm(o_origin[:,:2])
    n_o_target = o_target[:,:2] / norm(o_target[:,:2])
    origin_angle = np.arccos(n_o_origin[0,0])
    target_angle = np.arccos(n_o_target[0,0])

    # edge case where have the same XY coords
    if np.allclose(origin[:,:2],target[:,:2],atol=delta):
        complet_turns_angle = turns * 2 * np.pi
        remaining_angle = 0
    else:
        complet_turns_angle = (turns-1) * 2 * np.pi
        remaining_angle = - cw_sign * (origin_angle - target_angle)
        remaining_angle %= np.pi*2
    final_angle = origin_angle + complet_turns_angle + remaining_angle
    radius = norm(offset)    
    arc_length = final_angle * radius / 2
    z_length = (origin[:,2] - target[:,2])
    travel_length = arc_length+z_length
    n = int(np.abs(np.ceil(travel_length/delta)[0]))

    x = np.cos(cw_sign*np.linspace(origin_angle,final_angle,n))*norm(offset) + origin[:,0] + offset[:,0]
    y = np.sin(cw_sign*np.linspace(origin_angle,final_angle,n))*norm(offset) + origin[:,1] + offset[:,1]
    z = np.linspace(origin[:,2],target[:,2],x.shape[0])[:,0]

    return [ GCodeLinearMove(X=x,Y=y,Z=z) for x,y,z in zip(x,y,z)]

def LinearizePostProcessor(codes : List[GCode],machine : Machine = Machine(),delta : float = 1):
    for code in codes:
        if isinstance(code,GCodeArcMove):
            start = machine.abs_pos
            machine.process_gcodes(code)
            yield from linearize_arc(code,start,delta)
        else:
            machine.process_gcodes(code)
            yield code