import math
from types import MethodType
from typing import List

from pybehave.Elements.Element import Element
from pybehave.Elements.FanElement import FanElement
from pybehave.GUIs import Colors
from pybehave.GUIs.GUI import GUI

from pybehave.Elements.InfoBoxElement import InfoBoxElement
from pybehave.Events import PybEvents


class ERPGUI(GUI):

    def initialize(self):
        self.info_boxes = []

        self.pulse_count = 0
        ne = InfoBoxElement(self, 372, 125, 50, 15, "PULSES REMAINING", 'BOTTOM', [str(self.npulse)])
        self.info_boxes.append(ne)

        return [*self.info_boxes]

    def handle_event(self, event: PybEvents.PybEvent) -> None:
        super().handle_event(event)
        if isinstance(event, PybEvents.StartEvent):
            self.pulse_count = 0
            self.info_boxes[0].set_text([str(self.npulse - self.pulse_count)])
        elif isinstance(event, PybEvents.TimeoutEvent) and event.name == "pulse_sep":
            self.pulse_count += 1
            self.info_boxes[0].set_text([str(self.npulse - self.pulse_count)])
            