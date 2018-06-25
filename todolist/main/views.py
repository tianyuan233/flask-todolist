from collections import OrderedDict
from datetime import datetime, timedelta

from flask import render_template, redirect, url_for, request
from flask_login import current_user, login_required
from sqlalchemy import and_

from todolist import db
from todolist.main.forms import AddTask, AddProject
from todolist.models import Task, Titles, Project
from . import main


@main.before_request
def main_form():
    if current_user.is_authenticated:
        projectform = AddProject()
        if projectform.validate_on_submit():
            p = Project(name=projectform.name.data, user_id=current_user.id)
            db.session.add(p)
            return redirect(url_for(".index"))


@main.route("/", methods=["GET", "POST"])
@login_required
def index():
    now = datetime.now()
    default_timenode = datetime.now().strftime("%Y-%m-%d")
    projectform = AddProject()
    form = AddTask()
    today_tasks = current_user.tasks.filter(
        Task.timenode == datetime.now().strftime("%Y-%m-%d")
    ).all()
    overdue_tasks = current_user.tasks.filter(
        and_(Task.filish == False, Task.timenode < datetime.now().strftime("%Y-%m-%d"))
    ).all()

    titles = Titles.query.filter_by(user_id=current_user.id).all()
    project = Project.query.filter_by(user_id=current_user.id).all()

    return render_template(
        "today.html",
        now=now,
        projectform=projectform,
        today_tasks=today_tasks,
        overdue_tasks=overdue_tasks,
        form=form,
        default_timenode=default_timenode,
        titles=titles,
        project=project
    )


@main.route("/add-task", methods=["GET", "POST"])
@login_required
def add_task():
    form = AddTask()
    default_timenode = datetime.now().strftime("%Y-%m-%d")
    if form.validate_on_submit():
        t = Task(
            task=form.task.data,
            project=form.project.data,
            timenode=form.timenode.data,
            user_id=current_user.id,
        )
        if form.new_title.data:
            nt = Titles(title=form.new_title.data, user_id=current_user.id)
            db.session.add(nt)
            db.session.commit()
            t.title = nt.id
            db.session.add(t)
            db.session.commit()
            return redirect(url_for('main.index'))
        else:
            t.title = form.title.data
            db.session.add(t)
            db.session.commit()
            return redirect(url_for('main.index'))
    return render_template("add-task.html", form=form, default_timenode=default_timenode)


@main.route('/task/filish/<int:id>')
@login_required
def task_filish(id):
    task = Task.query.get_or_404(id)
    task.filish = True
    db.session.add(task)
    return redirect(request.referrer)


@main.route('/task/unfilish/<int:id>')
@login_required
def task_unfilish(id):
    task = Task.query.get_or_404(id)
    task.filish = False
    db.session.add(task)
    return redirect(request.referrer)


@main.route('/task/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def task_edit(id):
    task = Task.query.get_or_404(id)
    if request.method == 'GET':
        return redirect(url_for('.index'))
    if request.method == 'POST':
        task.task = request.form.get('task_task' + str(id))
        if request.form.get('project' + str(id)):
            task.project = request.form.get('project' + str(id))
        task.timenode = request.form.get('timenode' + str(id))
        task.priority = request.form.get('priority' + str(id))
        db.session.add(task)
    return redirect(request.referrer)


@main.route('/task/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def task_delete(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(request.referrer)


@main.route('/sevenday', methods=['GET', 'POST'])
@login_required
def sevenday():
    form = AddTask()
    projectform = AddProject()
    days = []
    for i in range(7):
        days.append((datetime.now() + timedelta(days=i)
                     ).strftime("%Y-%m-%d"))
    tasks7 = OrderedDict()
    for day in days:
        tasks7[day] = []
        for task in current_user.tasks.all():
            if task.timenode == day:
                tasks7[day].append(task)
    return render_template('seven-day.html', tasks7=tasks7, form=form,
                           projectform=projectform)

