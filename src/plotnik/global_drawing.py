# global_drawing.py


class GlobalDrawing:
    def __init__(self):
        self.drawing = None
        self.processes = []

    def set(self, drawing) -> None:
        if self.drawing is not None:
            raise ValueError('Global drawing has already been set')
        self.drawing = drawing

    def store_process(self, process) -> None:
        if self.drawing is None:
            raise ValueError('Global drawing is not set')
        self.processes.append(process)

    def release_processes(self):
        if self.drawing is None:
            raise ValueError('Global drawing is not set')
        for process in self.processes:
            self.drawing.add_process(process)
        self.processes = []

    def release_drawing(self):
        self.release_processes()

        drawing = self.drawing
        self.drawing = None
        self.processes = []

        return drawing

    def last_point(self):
        if self.drawing is None:
            raise ValueError('Global drawing is not set')
        if len(self.processes) == 0:
            return None
        return self.processes[-1].end


class GlobalDrawingSingleton:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = GlobalDrawing()
        return cls.instance


GLOBAL_DRAWING = GlobalDrawingSingleton()
