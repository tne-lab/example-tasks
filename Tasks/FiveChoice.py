import random
from enum import Enum

from pybehave.Components.BinaryInput import BinaryInput
from pybehave.Components.TimedToggle import TimedToggle
from pybehave.Components.Toggle import Toggle
from pybehave.Events import PybEvents
from pybehave.Tasks.Task import Task


# noinspection PyAttributeOutsideInit
class FiveChoice(Task):
    """@DynamicAttrs"""
    class States(Enum):
        INITIATION = 0
        INTER_TRIAL_INTERVAL = 1
        STIMULUS_ON = 2
        LIMITED_HOLD = 3
        POST_RESPONSE_INTERVAL = 4

    @staticmethod
    def get_components():
        return {
            "nose_pokes": [BinaryInput, BinaryInput, BinaryInput, BinaryInput, BinaryInput],
            "nose_poke_lights": [Toggle, Toggle, Toggle, Toggle, Toggle],
            "food_trough": [BinaryInput],
            "food": [TimedToggle],
            "food_light": [Toggle],
            "house_light": [Toggle]
        }

    @staticmethod
    def get_constants():
        return {
            'max_duration': 30,  # The max time the task can take in minutes
            'max_trials': 100,  # The maximum number of trials the rat can do
            'inter_trial_interval': 5,  # Time between initiation and stimulus presentation
            'stimulus_duration': 0.5,  # Time the stimulus is presented for
            'limited_hold_duration': 5,  # Time after stimulus presentation during which the rat can decide
            'post_response_interval': 5,  # Time after response before the rat can initiate again
            'sequence': [random.randint(0, 4) for _ in range(100)],  # Sequence of stimulus presentations
            'dispense_time': 0.7
        }

    @staticmethod
    def get_variables():
        return {
            "cur_trial": 0
        }

    def init_state(self):
        return self.States.INITIATION

    def start(self):
        self.set_timeout("task_complete", self.max_duration * 60, end_with_state=False)
        self.house_light.toggle(True)
        self.food_light.toggle(True)

    def stop(self):
        self.house_light.toggle(False)
        self.food_light.toggle(False)
        for light in self.nose_poke_lights:
            light.toggle(False)

    def all_states(self, event: PybEvents.PybEvent) -> bool:
        if isinstance(event, PybEvents.TimeoutEvent) and event.name == "task_complete":
            self.complete = True
            return True
        elif isinstance(event, PybEvents.GUIEvent) and event.name == "GUI_PELLET":
            self.food.toggle(self.dispense_time)
            return True
        return False

    def INITIATION(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.ComponentChangedEvent) and event.comp is self.food_trough and event.comp.state:  # Trial is initiated when the rat nosepokes the trough
            self.food_light.toggle(False)  # Turn the food light off
            self.change_state(self.States.INTER_TRIAL_INTERVAL)

    def INTER_TRIAL_INTERVAL(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            self.set_timeout("inter_trial_interval", self.inter_trial_interval)
        elif isinstance(event, PybEvents.ComponentChangedEvent) and any(map(lambda x: x is event.comp and event.comp.state, self.nose_pokes)):  # The rat failed to withold a response
            self.house_light.toggle(False)
            self.change_state(self.States.POST_RESPONSE_INTERVAL, {"response": "premature"})
        elif isinstance(event, PybEvents.TimeoutEvent) and event.name == 'inter_trial_interval':  # The rat waited the necessary time
            self.nose_poke_lights[self.sequence[self.cur_trial]].toggle(True)  # Turn the stimulus light on
            self.change_state(self.States.STIMULUS_ON)

    def STIMULUS_ON(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            self.set_timeout("stimulus_duration", self.stimulus_duration)
        elif isinstance(event, PybEvents.ComponentChangedEvent):
            for i, np in enumerate(self.nose_pokes):
                if np is event.comp and event.comp.state:
                    if i == self.sequence[self.cur_trial]:  # If the selection was correct, provide a reward
                        self.food.toggle(self.dispense_time)
                        metadata = {"response": "correct"}
                    else:
                        self.house_light.toggle(False)
                        metadata = {"response": "incorrect"}
                    self.nose_poke_lights[self.sequence[self.cur_trial]].toggle(False)  # Turn the stimulus light off
                    self.change_state(self.States.POST_RESPONSE_INTERVAL, metadata)
                    break
        elif isinstance(event, PybEvents.TimeoutEvent) and event.name == 'stimulus_duration':  # The stimulus was shown for the allotted time
            self.nose_poke_lights[self.sequence[self.cur_trial]].toggle(False)  # Turn the stimulus light off
            self.change_state(self.States.LIMITED_HOLD)

    def LIMITED_HOLD(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            self.set_timeout("limited_hold", self.limited_hold_duration)
        elif isinstance(event, PybEvents.ComponentChangedEvent):
            for i, np in enumerate(self.nose_pokes):
                if np is event.comp and event.comp.state:
                    if i == self.sequence[self.cur_trial]:  # If the selection was correct, provide a reward
                        self.food.toggle(self.dispense_time)
                        metadata = {"response": "correct"}
                    else:
                        self.house_light.toggle(False)
                        metadata = {"response": "incorrect"}
                    self.nose_poke_lights[self.sequence[self.cur_trial]].toggle(False)  # Turn the stimulus light off
                    self.change_state(self.States.POST_RESPONSE_INTERVAL, metadata)
                    break
        elif isinstance(event, PybEvents.TimeoutEvent) and event.name == 'limited_hold':  # The rat failed to respond
            self.house_light.toggle(False)
            self.change_state(self.States.POST_RESPONSE_INTERVAL, {"response": "none"})

    def POST_RESPONSE_INTERVAL(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            self.set_timeout("post_response_interval", self.post_response_interval)
        elif isinstance(event, PybEvents.TimeoutEvent) and event.name == 'post_response_interval':  # The post response period has ended
            self.house_light.toggle(True)
            self.change_state(self.States.INITIATION)
            self.food_light.toggle(True)  # Turn the food light on
            self.cur_trial += 1

    def is_complete(self):
        return self.cur_trial == self.max_trials
