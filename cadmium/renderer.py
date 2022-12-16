from cadmium.cadmium import Run,Operation
from sdf import SDF3,SDF2,sdf3
from more_itertools import windowed

class RendererParams:
    run : Run

@sdf3
def cut(tool : SDF2, a,b) -> SDF3 :
    pass

def Renderer(params : RendererParams):
    run : Run = params.run
    f : SDF3 = run.stock.shape
    for op in run.program.operations:
        tool : SDF3 = op.tool.shape
        segments = windowed(op.path(1),2)
        for segment in segments:
            f -= 