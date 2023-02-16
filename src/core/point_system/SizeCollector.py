from src.enums import StateMode
from dataclasses import dataclass


@dataclass()
class SizeCollector:
    __slots__ = ["state", "left_panel", "top_panel", "toolbar_panel", "right_panel", "bottom_panel"]

    def __init__(self, state: StateMode = StateMode.HOME):
        self.state: StateMode = state
        self.left_panel: int = 0
        self.top_panel: int = 20
        self.toolbar_panel: int = 40
        self.right_panel: int = 340
        self.bottom_panel: int = 20

    @property
    def draw_toolbar_panel(self) -> int:
        if self.state is StateMode.WORK:
            return self.left_panel
        else:
            return 0

    @property
    def menu_toolbar_panel(self) -> int:
        if self.state is StateMode.WORK:
            return self.top_panel + self.toolbar_panel
        else:
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
