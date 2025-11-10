#!/usr/bin/env python3
from __future__ import annotations
from sheet_stream import TableDocuments


# Sujeito notificador
class NotifyProvider(object):

    def __init__(self):
        self.__observers: list = []

    @property
    def observers(self) -> list:
        return self.__observers

    @observers.setter
    def observers(self, value: list) -> None:
        pass

    def add_observer(self, observer) -> None:
        self.__observers.append(observer)

    def send_notify(self, tb: TableDocuments) -> None:
        for obs in self.__observers:
            obs.receive_notify(tb)


# Sujeito Observador.
class Observer(object):

    def __init__(self):
        pass

    def receive_notify(self, notify: TableDocuments) -> None:
        pass

