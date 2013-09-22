#!/usr/bin/env python

import csv
from itertools import product
import os
import pprint
import sys

import flow
import local_settings
from user import User

def main(argv):
    with open(local_settings.shift_data) as f:
        sf = local_settings.shift_fields

        shift_requests = {}
        reader = csv.reader(f,)
        first = True
        for row in reader:
            if first:
                first = False
                continue
            shift = row[sf['shift']]
            shift_requests[shift] = {}
            for task_id in [t['id'] for t in local_settings.tasks]:
                value = row[sf[task_id]]
                shift_requests[shift][task_id] = 0 if value == '' else int(value)

    g = flow.FlowNetwork()

    g.add_vertex('source')
    g.add_vertex('sink')

    for date, time, task in product(local_settings.dates,
            local_settings.timeslots, local_settings.tasks):
        if not local_settings.shifts[date][time]:
            continue
        shift = '%s %s' % (date, time)
        shift_task = '%s %s' % (shift, task['id'])
        g.add_vertex(shift_task)
        g.add_edge(shift_task, 'sink', shift_requests[shift][task['id']])

    for f in os.listdir(local_settings.local_data):
        if not os.path.isdir(os.path.join(local_settings.local_data, f)):
            continue
        hours = 0
        with User(f) as u:
            if u.get_num_available() == 0:
                continue
            g.add_vertex(f)
            g.add_edge('source', f, u.get_num_available())
            for day in local_settings.shifts:
                for shift in [s for s in local_settings.timeslots if local_settings.shifts[day][s]]:
                    if u.get_available(day, shift):
                        available_slot = '%s %s %s' % (f, day, shift)
                        g.add_vertex(available_slot)
                        g.add_edge(f, available_slot, 1)
                        for task_id in [t['id'] for t in local_settings.tasks]:
                            if u.get_task_status(task_id):
                                g.add_edge(available_slot, '%s %s %s' % (day, shift, task_id), 1)

    pprint.pprint(g.adj)

    print g.max_flow('source', 'sink')

    pprint.pprint(g.flow)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
