from datetime import datetime

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


@main.route("/")
def index():
    now = datetime.now()
    edit_task_form = AddTask()
    projectform = AddProject()
    today_tasks = current_user.tasks.filter(
        Task.timenode == datetime.now().strftime("%Y-%m-%d")
    ).all()
    overdue_tasks = current_user.tasks.filter(
        and_(Task.filish == False, Task.timenode < datetime.now().strftime("%Y-%m-%d"))
    ).all()

    return render_template(
        "today.html",
        now=now,
        edit_task_form=edit_task_form,
        projectform=projectform,
        today_tasks=today_tasks,
        overdue_tasks=overdue_tasks,
    )


@main.route("/add-task", methods=["GET", "POST"])
def add_task():
    form = AddTask()
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
        else:
            t.title = form.title.data
            db.session.add(t)
            db.session.commit()
    return render_template("add-task.html", form=form)

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
def edit_task(id):
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