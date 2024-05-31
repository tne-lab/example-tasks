from enum import Enum

import numpy as np
from pybehave.Tasks.Task import Task
from pybehave.Components.Stimmer import Stimmer

from pybehave.Events.OENetworkLogger import OEEvent
from pybehave.Events import PybEvents


class ERP(Task):
    """@DynamicAttrs"""
    class States(Enum):
        START_RECORD = 0
        ERP = 1
        STOP_RECORD = 2

    @staticmethod
    def get_components():
        return {
            'stim': [Stimmer]
        }

    @staticmethod
    def get_constants():
        return {
            'ephys': False,
            'record_lockout': 4,
            'npulse': 5,
            'pulse_sep': 4,
            'stim_dur': 180,
            'period': 180,
            'amps': ([[1, -1]]),
            'pws': [90, 90]
        }

    @staticmethod
    def get_variables():
        return {
            "pulse_count": 0
        }

    def init_state(self):
        return self.States.START_RECORD

    def start(self):
        self.stim.parametrize(0, 1, self.stim_dur, self.period, np.array(self.amps), self.pws)
        if self.ephys:
            self.log_event(OEEvent("startRecording"))

    def START_RECORD(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            self.set_timeout("record_lockout", self.record_lockout)
        elif isinstance(event, PybEvents.TimeoutEvent) and event.name == "record_lockout":
            self.change_state(self.States.ERP)

    def ERP(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            self.set_timeout("pulse_sep", self.pulse_sep)
        elif isinstance(event, PybEvents.TimeoutEvent) and event.name == "pulse_sep":
            self.stim.start(0)
            self.pulse_count += 1
            if self.pulse_count == self.npulse:
                self.change_state(self.States.STOP_RECORD)
                if self.ephys:
                    self.log_event(OEEvent("stopRecording"))
            else:
                self.set_timeout("pulse_sep", self.pulse_sep)

    def STOP_RECORD(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            self.set_timeout("record_lockout", self.record_lockout)
        elif isinstance(event, PybEvents.TimeoutEvent) and event.name == "record_lockout":
            self.complete = True
