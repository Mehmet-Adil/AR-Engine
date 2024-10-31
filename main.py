import cv2
from border_logic import get_borders, flip_points
import conversions
import numpy as np


class Text:
    def __init__(self, letters, direction="RIGHT", speed=1):
        self.letters = letters
        self.direction = direction
        self.speed = speed

    def draw(self, frame, blue_origin, green_origin, red_origins, border_lines):
        for letter in self.letters:
            points = np.array([conversions.coords_to_pos(blue_origin[0], green_origin[0], red_origins, border_lines,
                                                         (x, y, z)) for x, y, z in letter.points], dtype=np.int32)
            cv2.fillPoly(frame, pts=[points], color=letter.color)

    def move(self):
        if self.direction == "RIGHT":
            for letter in self.letters:
                if max([i[0] for i in letter.points]) + self.speed >= 80:
                    self.direction = "LEFT"
                    return

            for letter in self.letters:
                for point in letter.points:
                    point[0] += self.speed

        elif self.direction == "LEFT":
            for letter in self.letters:
                if min([i[0] for i in letter.points]) - self.speed <= 0:
                    self.direction = "RIGHT"
                    return

            for letter in self.letters:
                for point in letter.points:
                    point[0] -= self.speed


class Letter:
    def __init__(self, letter, points, color):
        self.letter = letter
        self.points = points
        self.color = color

    def draw(self, frame, origins, border_lines):
        for point in self.points:
            pos = conversions.coords_to_pos(*origins, border_lines, point)
            cv2.circle(frame, pos, 1, self.color)


class Game:
    def __init__(self):
        self.cam = cv2.VideoCapture(1)
        self.cam_height, self.cam_width = self.cam.read()[1].shape[:2]

        self.field_width = 80
        self.field_height = 40

    @staticmethod
    def draw_borders(frame, borders, border_lines):
        for border in borders:
            cv2.circle(frame, border, 3, (0, 0, 0))

        for line in border_lines:
            cv2.line(frame, line[0], line[1], (255, 255, 255), 3)

    def main_loop(self):
        m_left = Letter("m_left", [[0, 0, 0], [0, 0, 8], [2, 0, 8], [2, 0, 0]], [52, 11, 162])
        m_middle = Letter("m_middle", [[3, 0, 2], [3, 0, 8], [5, 0, 8], [5, 0, 2]], [52, 11, 162])
        m_right = Letter("m_right", [[6, 0, 0], [6, 0, 8], [8, 0, 8], [8, 0, 0]], [52, 11, 162])
        i_top = Letter("i_top", [[10, 0, 6], [10, 0, 8], [12, 0, 8], [12, 0, 6]], [52, 11, 162])
        i_bottom = Letter("i_bottom", [[10, 0, 0], [10, 0, 5], [12, 0, 5], [12, 0, 0]], [159, 152, 155])
        t_top = Letter("t_top", [[14, 0, 6], [14, 0, 8], [19, 0, 8], [19, 0, 6]], [52, 11, 162])
        t_bottom = Letter("t_bottom", [[14, 0, 0], [14, 0, 5], [16, 0, 5], [16, 0, 0]], [52, 11, 162])

        mit_text = Text([m_left, m_middle, m_right, i_top, i_bottom, t_top, t_bottom])

        m_left = Letter("m_left", [[61 + 0, 20, 0], [61 + 0, 20, 8], [61 + 2, 20, 8], [61 + 2, 20, 0]], [52, 11, 162])
        m_middle = Letter("m_middle", [[61 + 3, 20, 2], [61 + 3, 20, 8], [61 + 5, 20, 8], [61 + 5, 20, 2]], [52, 11, 162])
        m_right = Letter("m_right", [[61 + 6, 20, 0], [61 + 6, 20, 8], [61 + 8, 20, 8], [61 + 8, 20, 0]], [52, 11, 162])
        i_top = Letter("i_top", [[61 + 10, 20, 6], [61 + 10, 20, 8], [61 + 12, 20, 8], [61 + 12, 20, 6]], [52, 11, 162])
        i_bottom = Letter("i_bottom", [[61 + 10, 20, 0], [61 + 10, 20, 5], [61 + 12, 20, 5], [61 + 12, 20, 0]], [159, 152, 155])
        t_top = Letter("t_top", [[61 + 14, 20, 6], [61 + 14, 20, 8], [61 + 19, 20, 8], [61 + 19, 20, 6]], [52, 11, 162])
        t_bottom = Letter("t_bottom", [[61 + 14, 20, 0], [61 + 14, 20, 5], [61 + 16, 20, 5], [61 + 16, 20, 0]], [52, 11, 162])

        mit_text2 = Text([m_left, m_middle, m_right, i_top, i_bottom, t_top, t_bottom], direction="LEFT")

        decoration_text = Text([Letter("green wall", [[0, 40, 0], [0, 40, 10], [80, 40, 10], [80, 40, 0]], color=[52, 162, 14])])

        while True:
            _, frame = self.cam.read()

            blue_origin, green_origin, red_origins, border_lines = get_borders(frame)
            borders = blue_origin + green_origin + red_origins

            self.draw_borders(frame, borders, border_lines)

            for col in range(self.field_width):
                for row in range(self.field_height):
                    if len(border_lines) != 4:
                        break

                    pos = conversions.coords_to_pos(blue_origin[0], green_origin[0], red_origins, border_lines,
                                                    (col, row, 0))
                    cv2.circle(frame, pos, 1, (255, 255, 255))

            try:
                decoration_text.draw(frame, blue_origin, green_origin, red_origins, border_lines)

                mit_text2.draw(frame, blue_origin, green_origin, red_origins, border_lines)
                mit_text2.move()

                mit_text.draw(frame, blue_origin, green_origin, red_origins, border_lines)
                mit_text.move()
            except Exception as e:
                print(e)

            try:
                cv2.putText(frame, str(flip_points(blue_origin, self.cam_width, self.cam_height)[0]), blue_origin[0],
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            except Exception as e:
                print(e)

            self.event_control()

            cv2.imshow("Game", frame)

    def event_control(self):
        key = cv2.waitKey(10)

        if key == 27:  # exit on ESC
            self.quit_game()

    def quit_game(self):
        cv2.destroyAllWindows()
        self.cam.release()
        quit()


if __name__ == "__main__":
    game = Game()
    game.main_loop()
