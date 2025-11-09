#!/usr/bin/env python3
from __future__ import annotations
from sheet_stream import TableDocuments


# Sujeito notificador
class NotifyProvider(object):

    def __init__(self):
        self.observers: list = []

    def add_observer(self, observer) -> None:
        self.observers.append(observer)

    def send_notify(self, tb: TableDocuments) -> None:
        for obs in self.observers:
            obs.receive_notify(tb)


# Sujeito Observador.
class Observer(object):

    def __init__(self):
        pass

    def receive_notify(self, notify: TableDocuments) -> None:
        pass

