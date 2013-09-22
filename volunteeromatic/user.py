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

class BadTaskId(KeyError):
    pass

class User(object):
    def __init__(self, username):
        self._username = username
        self._userpath = self._path(username)
        self._file = None

    def __enter__(self):
        try:
            with open(self._filename()) as f:
                data = json.load(f)
                self._available = data['available']
                self._tasks = data['tasks']
        except IOError:
            self._create_account()
            self._initialize_availability()
            self._initialize_tasks()
        return self

    def __exit__(self, type, value, exception):
        with open(self._filename(), 'w') as f:
            data = {
                    'available': self._available,
                    'tasks': self._tasks
                }
            json.dump(data, f)

    def get_task_status(self, task_id):
        if task_id not in self._tasks:
            raise BadTaskID('task id: %s' % task_id)

        return self._tasks.get(task_id, True)

    def set_task_status(self, task_id, value):
        if task_id not in self._tasks:
            raise BadTaskID('task id: %s' % task_id)
        if value not in (True, False):
            raise RuntimeError('value not in {T,F}')

        self._tasks[task_id] = value

    def get_available(self, day, shift):
        if day not in local_settings.shifts:
            raise BadDateKey('day: %s' % day)
        if shift not in local_settings.timeslots:
            raise BadSlotKey('day: %s  slot: %s' % (day, shift))
        if not local_settings.shifts[day][shift]:
            raise InvalidSlot('day: %s  slot: %s' % (day, shift))

        return self._available.get(day, {}).get(shift, False)

    def set_available(self, day, shift, value):
        if day not in local_settings.shifts:
            raise BadDateKey('day: %s' % day)
        if shift not in local_settings.timeslots:
            raise BadSlotKey('day: %s  slot: %s' % (day, shift))
        if not local_settings.shifts[day][shift]:
            raise InvalidSlot('day: %s  slot: %s' % (day, shift))

        self._available[day][shift] = value
        return

    def get_num_available(self):
        n = 0
        for day in self._available:
            for shift in self._available[day]:
                if self._available[day][shift]:
                    n += 1
        return n


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

    def _initialize_tasks(self):
        self._tasks = {}

        for task in local_settings.tasks:
            self._tasks[task['id']] = True


