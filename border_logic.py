import cv2
import numpy as np
from math import atan2


def get_pixels_of_color(img, l1, u1, l2=None, u2=None):
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # lower mask (0-10)
    lower_color = np.array(l1)
    upper_color = np.array(u1)
    mask0 = cv2.inRange(img_hsv, lower_color, upper_color)

    if l2 and u2:
        # upper mask (170-180)
        lower_color = np.array(l2)
        upper_color = np.array(u2)
        mask1 = cv2.inRange(img_hsv, lower_color, upper_color)

        return mask0 + mask1

    return mask0


def angle_from_centroid(vertex, centroid_x, centroid_y):
    """Returns the angle from the center"""

    return atan2(vertex[1] - centroid_y, vertex[0] - centroid_x)


def sort_vertices(vertices):
    # Calculate the centroid of the polygon (average of x and y coordinates)
    centroid_x = sum([v[0] for v in vertices]) / len(vertices)
    centroid_y = sum([v[1] for v in vertices]) / len(vertices)

    # Sort vertices by the angle from centroid
    return sorted(vertices, key=lambda i: angle_from_centroid(i, centroid_x, centroid_y))


def group_vertices_as_lines(vertices):
    if not len(vertices):
        return []

    sorted_vertices = sort_vertices(vertices)

    lines = []

    for i in range(len(sorted_vertices)):
        # Create a line between the current vertex and the next (cyclically)
        line = (sorted_vertices[i], sorted_vertices[(i + 1) % len(sorted_vertices)])
        lines.append(line)

    return lines


def get_centers_from_mask(mask_, min_area=50, n_largest=None, normalise_pos=True):
    contours, _ = cv2.findContours(mask_, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_contour_area = min_area  # Define your minimum area threshold
    large_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]
    if n_largest:
        large_contours = get_n_largest_contours(large_contours, n_largest)

    centers = []

    for contour in large_contours:
        moments = cv2.moments(contour)
        centers.append((0 if not moments['m00'] else int(moments['m10'] / moments['m00']),
                        0 if not moments['m00'] else int(moments['m01'] / moments['m00'])))

    return centers, large_contours


def flip_points(points, screen_width, screen_height, direction="HORIZONTAL"):
    out = []

    for point in points:
        if direction == "HORIZONTAL":
            out.append((point[0], screen_height - point[1]))
        elif direction == "VERTICAL":
            out.append((screen_width - point[0], point[1]))
        elif direction == "BOTH":
            out.append((screen_width - point[0], screen_height - point[1]))
        else:
            out.append(point)

    return out


def smoothen_mask(mask):
    retval, mask_thresh = cv2.threshold(mask, 180, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    new_mask = cv2.morphologyEx(mask_thresh, cv2.MORPH_OPEN, kernel)

    return new_mask


def get_n_largest_contours(contours, n):
    contour_areas = [(cv2.contourArea(c), c) for c in contours]
    largest_contours = sorted(contour_areas, reverse=True, key=lambda x: x[0])[:n]

    return [i[1] for i in largest_contours]


def filter_irregular_shapes(origins, contours):
    filtered_origins = []

    for cnt, center in zip(contours, origins):
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * (area / (perimeter ** 2))

        # Keep only contours that are large enough and have low circularity (to filter hands)
        if area > 500 and circularity < 0.9:
            filtered_origins.append(center)

    return filtered_origins


def get_borders(frame):
    red_origins_mask = get_pixels_of_color(frame, [0, 120, 120], [10, 255, 255], [170, 120, 120],
                                           [180, 255, 255])  # For 2 red vertices
    red_origins_mask = smoothen_mask(red_origins_mask)
    red_origins, red_contours = get_centers_from_mask(red_origins_mask, n_largest=2)
    red_origins = filter_irregular_shapes(red_origins, red_contours)

    blue_origin_mask = get_pixels_of_color(frame, [90, 40, 60], [110, 255, 255])  # For blue origin
    blue_origin_mask = smoothen_mask(blue_origin_mask)
    blue_origin, blue_contour = get_centers_from_mask(blue_origin_mask, n_largest=1)
    blue_origin = filter_irregular_shapes(blue_origin, blue_contour)

    green_origin_mask = get_pixels_of_color(frame, [35, 50, 50], [85, 255, 255])  # For green origin
    green_origin_mask = smoothen_mask(green_origin_mask)
    green_origin, green_contour = get_centers_from_mask(green_origin_mask, n_largest=1)
    green_origin = filter_irregular_shapes(green_origin, green_contour)

    borders = blue_origin + green_origin + red_origins

    if len(borders) != 4:
        return (), (), (), ()

    rect_lines = group_vertices_as_lines(borders)

    return blue_origin, green_origin, red_origins, rect_lines
