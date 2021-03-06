#!/usr/bin/env python

import json
import sys

from flask import Flask
from flask import abort
from flask import render_template
from flask import request

from user import User
import local_settings

app = Flask(__name__)
app.debug = True

def process_avail(user, avail):
    for shift in avail:
        d_,t_ = shift.split('|')
        d = d_.replace('_', ' ')
        t = t_.replace('_', ' ')
        user.set_available(d, t, avail[shift])

def process_tasks(user, all_tasks):
    for task in all_tasks:
        user.set_task_status(task['id'], request.form.get(task['id']) == 'on')

@app.route('/', methods=['GET', 'POST'])
def index():
    uniqname = request.headers.get('X_REMOTE_USER')
    if uniqname is None:
        if app.debug:
            uniqname = 'marysuec'
        else:
            abort(403)

    if request.method == 'GET':
        with User(uniqname) as u:
            return render_template('index.html',
                uniqname=uniqname,
                timeslots=local_settings.timeslots,
                dates=local_settings.dates,
                shifts=local_settings.shifts,
                tasks=local_settings.tasks,
                user=u)

    elif request.method == 'POST':
        with User(uniqname) as u:
            app.logger.debug(request.form)
            user_json = request.form.get('schedule_data')
            if not user_json:
                abort(400)
            user_avail = json.loads(user_json)
            if not user_avail:
                abort(400)
            process_avail(u, user_avail)
            process_tasks(u, local_settings.tasks)

        # sloppy but don't care
        with User(uniqname) as u:
            return render_template('index.html',
                flash='Thanks!',
                uniqname=uniqname,
                timeslots=local_settings.timeslots,
                dates=local_settings.dates,
                shifts=local_settings.shifts,
                tasks=local_settings.tasks,
                user=u)
    else:
        abort(500)

if __name__ == '__main__':
    app.run(host='127.0.0.1',port=5001)

