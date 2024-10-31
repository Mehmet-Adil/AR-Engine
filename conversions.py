import numpy as np
import cv2


def coords_to_pos(blue_origin, green_origin, red_origins, border_lines, coords, z_multiplier=20):
    """
    Convert 3D real-world coordinates (x, y, z) into 2D screen coordinates (x_screen, y_screen).
    """
    if len(border_lines) != 4:
        return None

    # Real-world coordinates of the corners (in your game field)
    real_corners = np.array([
        [0, 0],      # Blue origin (bottom-left)
        [0, 40],     # Green origin (top-left)
        [80, 0],     # Red origin (bottom-right)
        [80, 40]     # Red origin (top-right)
    ], dtype="float32")

    # Detected corner positions on the camera screen (from the blue, green, red origins)
    screen_corners = np.array([
        blue_origin,
        green_origin,
        red_origins[0],
        red_origins[1]
    ], dtype="float32")

    homography_matrix, _ = cv2.findHomography(real_corners, screen_corners)
    real_point = np.array([[coords[0], coords[1]]], dtype="float32").reshape(-1, 1, 2)
    screen_point = cv2.perspectiveTransform(real_point, homography_matrix)

    x_screen, y_screen = screen_point[0][0]

    z_offset = coords[2] * z_multiplier
    y_screen -= z_offset  # Subtract the z_offset from y to simulate height

    return int(x_screen), int(y_screen)
