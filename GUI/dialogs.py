from .basic_widgets import BasicDialog


class MoveDialog(BasicDialog):
    def __init__(self, parent=None):
        super().__init__(parent, title="整体移动na图纸", hide_bottom=True)

    def ensure(self):
        self.close()


class ScaleDialog(BasicDialog):
    def __init__(self, parent=None):
        super().__init__(parent, title="整体缩放na图纸", hide_bottom=True)

    def ensure(self):
        self.close()
