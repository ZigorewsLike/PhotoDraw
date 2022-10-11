class Point3d:
    def __init__(self, x=0., y=0., z=0.):
        self.x: float = x
        self.y: float = y
        self.z: float = z

    def __str__(self):
        return f"Point3d({self.x}, {self.y}, {self.z})"

    def __truediv__(self, other):
        if not isinstance(other, Point3d):
            return Point3d(self.x / other, self.y / other, self.z / other)
        return Point3d(self.x / other.x, self.y / other.y, self.z / other.z)

    def __itruediv__(self, other):
        if not isinstance(other, Point3d):
            return Point3d(self.x / other, self.y / other, self.z / other)
        return Point3d(self.x / other.x, self.y / other.y, self.z / other.z)

    def from_str(self, string: str) -> None:
        string_array = string.replace("Point3d(", "").replace(")", "").split(', ')
        self.x, self.y, self.z = [float(val) for val in string_array]
