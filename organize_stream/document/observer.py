#!/usr/bin/env python3
from __future__ import annotations
import convert_stream as cs


# Sujeito notificador
class NotifyProvider(object):

    def __init__(self):
        self.observers: list = []

    def add_observer(self, observer) -> None:
        self.observers.append(observer)

    def send_notify(self, tb: cs.TextTable) -> None:
        for obs in self.observers:
            obs.receive_notify(tb)


# Sujeito Observador.
class Observer(object):

    def __init__(self):
        pass

    def receive_notify(self, notify: cs.TextTable) -> None:
        pass

