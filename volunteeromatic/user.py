#!/usr/bin/env python

import json
import os

import local_settings

class InvalidSlot(RuntimeError):
    pass

class BadSlotKey(KeyError):
    pass

class BadDateKey(KeyError):
    pass

class User(object):
    def __init__(self, username):
        self._username = username
        self._userpath = self._path(username)
        self._file = None

    def __enter__(self):
        try:
            with open(self._filename()) as f:
                self._available = json.load(f)
        except IOError:
            self._create_account()
            self._initialize_availability()
        return self

    def __exit__(self, type, value, exception):
        with open(self._filename(), 'w') as f:
            json.dump(self._available, f)

    def get_available(self, day, shift):
        if day not in local_settings.shifts:
            raise BadDateKey('day: %s' % day)
        if shift not in local_settings.timeslots:
            raise BadSlotKey('day: %s  slot: %s' % (day, shift))
        if not local_settings.shifts[day][shift]:
            raise InvalidSlot('day: %s  slot: %s' % (day, shift))

        return self._available[day][shift]

    def set_available(self, day, shift, value):
        if day not in local_settings.shifts:
            raise BadDateKey('day: %s' % day)
        if shift not in local_settings.timeslots:
            raise BadSlotKey('day: %s  slot: %s' % (day, shift))
        if not local_settings.shifts[day][shift]:
            raise InvalidSlot('day: %s  slot: %s' % (day, shift))

        self._available[day][shift] = value
        return

    def _filename(self):
        return os.path.join(self._userpath, 'data.json')

    def _path(self, username):
        return os.path.join(local_settings.local_data,
                username)

    def _exists(self):
        return os.path.isdir(self._userpath)

    def _create_account(self):
        os.mkdir(self._userpath)

    def _initialize_availability(self):
        self._available = {}
        shifts = local_settings.shifts
        timeslots = local_settings.timeslots

        for day in shifts:
            for shift in timeslots:
                if shifts[day][shift]:
                    try:
                        self._available[day][shift] = False
                    except KeyError:
                        self._available[day] = {shift: False}


