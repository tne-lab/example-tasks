from enum import Enum

from pybehave.Elements.CircleLightElement import CircleLightElement
from pybehave.Elements.FoodLightElement import FoodLightElement
from pybehave.Elements.NosePokeElement import NosePokeElement
from pybehave.Elements.ButtonElement import ButtonElement
from pybehave.Elements.InfoBoxElement import InfoBoxElement
from pybehave.Events import PybEvents
from pybehave.GUIs.GUI import GUI


# noinspection PyAttributeOutsideInit
class FiveChoiceGUI(GUI):
    """@DynamicAttrs"""
    class Events(Enum):
        GUI_PELLET = 0

    def initialize(self):
        self.np_lights = []
        self.np_inputs = []
        for i in range(5):
            npl = CircleLightElement(self, 50 + i * (25 + 60), 60, 30, comp=self.nose_poke_lights[-i - 1])
            self.np_lights.append(npl)
            npi = NosePokeElement(self, 50 + i * (25 + 60), 150, 30, comp=self.nose_pokes[-i - 1])
            self.np_inputs.append(npi)

        self.food_poke = NosePokeElement(self, 220, 360, 30, comp=self.food_trough)
        self.feed_button = ButtonElement(self, 200, 520, 100, 40, "FEED", f_size=28)
        self.feed_button.mouse_up = lambda _: self.log_gui_event(self.Events.GUI_PELLET)
        self.pellets = InfoBoxElement(self, 200, 440, 100, 30, "PELLETS", 'BOTTOM', ['0'], f_size=28)
        self.time_in_task = InfoBoxElement(self, 375, 580, 100, 30, "TIME", 'BOTTOM', ['0'], f_size=28)
        self.trial_count = InfoBoxElement(self, 375, 500, 100, 30, "TRIAL", 'BOTTOM', ['0'], f_size=28)
        self.fle = FoodLightElement(self, 200, 250, 100, 90, comp=self.food_light)
        self.fte = NosePokeElement(self, 220, 340, 30, comp=self.food_trough)

        return [*self.np_lights, *self.np_inputs, self.feed_button, self.pellets, self.time_in_task, self.trial_count,
                self.fle, self.fte]

    def handle_event(self, event: PybEvents.PybEvent) -> None:
        super(FiveChoiceGUI, self).handle_event(event)
        self.time_in_task.set_text(str(round(self.time_elapsed / 60, 2)))
        if isinstance(event, PybEvents.StartEvent):
            self.food.count = 0
            self.pellets.set_text(str(self.food.count))
            self.trial_count.set_text("1")
        elif isinstance(event, PybEvents.ComponentUpdateEvent) and event.comp_id == self.food.id and event.value:
            self.food.count += 1
            self.pellets.set_text(str(self.food.count))
        elif isinstance(event, PybEvents.StateExitEvent) and event.name == "POST_RESPONSE_INTERVAL":
            self.cur_trial += 1
            self.trial_count.set_text(str(self.cur_trial + 1))
