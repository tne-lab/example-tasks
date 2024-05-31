from enum import Enum
import math

from pybehave.Elements.BarPressElement import BarPressElement
from pybehave.Elements.ButtonElement import ButtonElement
from pybehave.Elements.InfoBoxElement import InfoBoxElement
from pybehave.Events import PybEvents
from pybehave.GUIs.GUI import GUI


# noinspection PyAttributeOutsideInit
class BarPressGUI(GUI):
    """@DynamicAttrs"""
    class Events(Enum):
        GUI_PELLET = 0

    def initialize(self):
        self.lever = BarPressElement(self, 77, 25, 100, 90, comp=self.food_lever)
        self.feed_button = ButtonElement(self, 129, 170, 50, 20, "FEED")
        self.feed_button.mouse_up = lambda _: self.log_gui_event(self.Events.GUI_PELLET)
        self.presses = InfoBoxElement(self, 69, 125, 50, 15, "PRESSES", 'BOTTOM', ['0'])
        self.pellets = InfoBoxElement(self, 129, 125, 50, 15, "PELLETS", 'BOTTOM', ['0'])
        self.time_in_task = InfoBoxElement(self, 372, 170, 50, 15, "TIME", 'BOTTOM', ['0'])
        self.vic = InfoBoxElement(self, 64, 170, 50, 15, "VI COUNT", 'BOTTOM', ['0'])
        self.n_press = 0

        return [self.lever, self.feed_button, self.presses, self.pellets, self.time_in_task, self.vic]

    def handle_event(self, event: PybEvents.PybEvent) -> None:
        super().handle_event(event)
        self.time_in_task.set_text(str(round(self.time_elapsed / 60, 2)))
        if isinstance(event, PybEvents.StartEvent):
            self.food.count = 0
            self.n_press = 0
            self.pellets.set_text(str(self.food.count))
            self.presses.set_text(str(self.n_press))
        elif isinstance(event, PybEvents.ComponentUpdateEvent) and event.comp_id == self.food.id and event.value:
            self.food.count += 1
            self.pellets.set_text(str(self.food.count))
        elif isinstance(event, PybEvents.ComponentUpdateEvent) and event.comp_id == self.food_lever.id and event.value:
            self.n_press += 1
            self.presses.set_text(str(self.n_press))
        elif isinstance(event, PybEvents.StateEnterEvent) and event.name == "REWARD_UNAVAILABLE":
            self.lockout = event.metadata['lockout']

        if self.state == "REWARD_UNAVAILABLE":
            self.vic.set_text([str(max([0, math.ceil(self.lockout - self.time_in_state)]))])
        else:
            self.vic.set_text("0")
