from turtle import *
import fitz  # PyMuPDF
import pymupdf
from random import random

def extract_shapes(pdf_path):
    print("Extracting shapes...")
    doc = pymupdf.open(pdf_path)
    print("Just opened a doc", type(doc), doc)
    page = doc[0]
    paths = page.get_drawings()  # extract existing drawings
    print("Extracted shapes")
    return paths

def pdf_output(paths, w, h, name='unnamed'):
    outpdf = pymupdf.open()
    outpage = outpdf.new_page(width=w, height=h)
    shape = outpage.new_shape()  # make a drawing canvas for the output page
    # --------------------------------------
    # loop through the paths and draw them
    # --------------------------------------
    for path in paths:
        pf = (0, 0, 0)
        for i in range(len(path) - 1):
            shape.draw_line(path[i], path[i+1])
        #shape.draw(path[-1], path[0])
        # ------------------------------------------------------
        shape.finish(
            fill=(random(), random(), random()),  # fill color
            color=pf,  # line color
            dashes=None,  # line dashing
            even_odd=False,  # control color of overlaps
            closePath=True,  # whether to connect last and first point
            lineJoin=0,  # how line joins should look like
            lineCap=0,  # how line ends should look like
            width=1,  # line width
            stroke_opacity=1,  # same value for both
            fill_opacity=1,  # opacity parameters
            )
    # all paths processed - commit the shape to its page
    shape.commit()
    outpdf.save(name)

def pdf_input(paths):
    polys = []
    for path in paths:
        print(path['items'])
        points = []
        for item in path['items']:
            if item[0] == "l":
                points.append((item[1][0], item[1][1]))
        polys.append(points)
    for popol in polys:
        for pol in popol:
            print(pol, end=', ')
            #goto(pol[0], pol[1])
            #down()
        print()
    return polys