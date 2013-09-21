#!/usr/bin/env python

import os
import sys

import local_settings
from user import User

def main(argv):
    shifts = {}

    for uniqname in [f for f in os.listdir(local_settings.local_data)
            if os.path.isdir(os.path.join(local_settings.local_data, f))]:
        with User(uniqname) as u:
            for day in local_settings.shifts:
                for shift in [s for s in local_settings.timeslots if local_settings.shifts[day][s]]:
                    if u.get_available(day, shift):
                        try:
                            shifts[day][shift] += 1
                        except KeyError:
                            try:
                                shifts[day][shift] = 1
                            except KeyError:
                                shifts[day] = {shift: 1}
                    else:
                        try:
                            shifts[day][shift] += 0
                        except KeyError:
                            try:
                                shifts[day][shift] = 0
                            except KeyError:
                                shifts[day] = {shift: 0}


    for day in local_settings.dates:
        print '***%s***' % day
        for shift in [s for s in local_settings.timeslots if local_settings.shifts[day][s]]:
            print '  %s: %d' % (shift, shifts[day][shift])




if __name__ == '__main__':
    sys.exit(main(sys.argv))
