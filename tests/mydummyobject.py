from __future__ import annotations


class MyDummyObject:
    def __init__(self, x: int, y: int, nested: MyDummyObject | None = None):
        self.x = x
        self.y = y
        self.nested = nested

    def __repr__(self):
        return f"MyDummyObject(x={self.x}, y={self.y}, nested={self.nested})"