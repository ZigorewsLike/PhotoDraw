from src.enums import StateMode


class SizeCollector:
    left_panel: int = 0
    top_panel: int = 20 + 40
    right_panel: int = 0
    bottom_panel: int = 20

    def __init__(self, state: StateMode = StateMode.HOME):
        self.state: StateMode = state

    @property
    def draw_toolbar_panel(self) -> int:
        if self.state is StateMode.WORK:
            return self.left_panel
        else:
            return 0

    @property
    def menu_toolbar_panel(self) -> int:
        return self.top_panel

    @property
    def correction_panel(self) -> int:
        if self.state is StateMode.WORK:
            return self.right_panel
        else:
            return 0

    @property
    def footer_panel(self) -> int:
        return self.bottom_panel
