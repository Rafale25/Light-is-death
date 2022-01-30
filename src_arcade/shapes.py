from math import radians, cos, sin

class ShapeBuilder:
    def quad():
        vertices = [
            -0.5, 0.5,
            -0.5, -0.5,
            0.5, -0.5,

            0.5, -0.5,
            0.5, 0.5,
            -0.5, 0.5,
        ]
        return vertices

    def disk(n=128):
        vertices = []

        inc = radians(360.0 / n)

        for i in range(n):
            x = cos(inc * i)
            y = sin(inc * i)
            vertices.extend((x, y))

        return vertices
