from shapely.geometry import Polygon, Point
from pyckingsolver import InstanceBuilder, Objective, Solver
from tools.pdf import pdf_input, extract_shapes, pdf_output
from turtle import *
import fitz  # PyMuPDF
import pymupdf

def pypack(path, w, h, name='unnamed', copies=1, time_limit=1):
    polys=pdf_input(extract_shapes(path))

    b = InstanceBuilder(Objective.OPEN_DIMENSION_Y)
    b.add_bin_type_rectangle(w, h)

    for poly in polys:
        b.add_item_type(Polygon(poly), allowed_rotations=[(0, 360)], copies=copies)

    solver = Solver()  # auto-finds bundled binary
    solution = solver.solve(b.build(), time_limit=time_limit)
    solution_met = [list(item.shapes[0].exterior.coords) for item in solution.all_items()]
    pdf_output(solution_met, w, h, name=name)
    print(f"{solution.total_item_count()} items in {solution.total_bins_used()} bins")

def turtle_vis(solution):
    speed(0)
    up()
    for item in solution:
        for point in item:
            goto(point[0]- 250, point[1] - 250)
            down()
        up()
    input()

if __name__ == '__main__':
    pypack("C:/Users/Иван/Documents/low_poly1.pdf", 500, 500, name="solution_met.pdf", copies=5, time_limit=15)