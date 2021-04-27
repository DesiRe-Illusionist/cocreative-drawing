import cv2
import numpy
import feature_extraction

def evaluate(cur_canvas, stroke_candidates, feature_set):

    max_score = float('-inf')
    max_agent = ''

    for agent in stroke_candidates:
        agent_stroke, _ = stroke_candidates[agent]

        hypothetical_canvas = draw_stroke_on_img(cur_canvas, agent_stroke, 600, 600)

        canvas_num_components, canvas_center_of_mass, canvas_components, white_space = feature_extraction.findConnectedComponents(hypothetical_canvas)
        new_contours, _ = feature_extraction.findContours(hypothetical_canvas)
        old_contours, _ = feature_extraction.findContours(cur_canvas)

        contour_delta = len(new_contours) - len(old_contours)
        com_from_center_x = abs(canvas_center_of_mass[0] - 300) / 100
        com_from_center_y = abs(canvas_center_of_mass[1] - 300) / 100

        eval_features_val = numpy.array([contour_delta, com_from_center_x, com_from_center_y])
        eval_features_weight = numpy.array([-10, -2, -2])

        eval = numpy.dot(eval_features_val, eval_features_weight)

        if eval > max_score:
            max_score = eval
            max_agent = agent
    
    return max_agent


def draw_stroke_on_img(image, stroke, width, height):
    new_image = cv2.resize(image, (width, height))
    for i in range(len(stroke)):
        for j in range(len(stroke[i]) - 1):
            cv2.line(new_image, (int(stroke[i][j][0]), int(stroke[i][j][1])), (int(stroke[i][j+1][0]), int(stroke[i][j+1][1])), (0, 0, 0), 5)
    return new_image