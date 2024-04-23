# global_drawing.py

class GlobalDrawing:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.drawing = None

    def set_drawing(self, drawing):
        self.drawing = drawing

    def add_process(self, process):
        if self.drawing:
            self.drawing.add_process(process)
        else:
            raise Exception("Drawing is not set.")

def setup_drawing():
    from .drawing import Drawing
    gd = GlobalDrawing.get_instance()
    new_drawing = Drawing()
    #new_drawing.initialize_axes()  # Инициализируем оси
    gd.set_drawing(new_drawing)
    return gd.drawing
