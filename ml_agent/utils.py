import tensorflow as tf
import svgwrite
from IPython.display import SVG, display


def get_bounds(data, factor=10):
    """Return bounds of data."""
    min_x = 0
    max_x = 0
    min_y = 0
    max_y = 0

    abs_x = 0
    abs_y = 0
    for i in range(len(data)):
        x = float(data[i, 0]) / factor
        y = float(data[i, 1]) / factor
        abs_x += x
        abs_y += y
        min_x = min(min_x, abs_x)
        min_y = min(min_y, abs_y)
        max_x = max(max_x, abs_x)
        max_y = max(max_y, abs_y)

    return (min_x, max_x, min_y, max_y)


def draw_strokes(data, factor=0.2, svg_filename="sample.svg"):
    min_x, max_x, min_y, max_y = get_bounds(data, factor)
    dims = (200 + max_x - min_x, 200 + max_y - min_y)
    dwg = svgwrite.Drawing(svg_filename, size=dims)
    dwg.add(dwg.rect(insert=(0, 0), size=dims, fill="white"))
    lift_pen = 1
    abs_x = (100 + max_x - min_x) / 2
    abs_y = (100 + max_y - min_y) / 2
    p = "M%s,%s " % (abs_x, abs_y)
    command = "m"
    for i in range(len(data)):
        if lift_pen == 1:
            command = "m"
        elif command != "l":
            command = "l"
        else:
            command = ""
        x = float(data[i, 0]) / factor
        y = float(data[i, 1]) / factor
        lift_pen = data[i, 2]
        p += command + str(x) + "," + str(y) + " "
    the_color = "black"
    stroke_width = 1
    dwg.add(dwg.path(p).stroke(the_color, stroke_width).fill("none"))
    dwg.save()
    display(SVG(dwg.tostring()))
