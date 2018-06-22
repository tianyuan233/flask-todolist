from datetime import datetime

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Required, Length, Optional, DataRequired


class AddProject(FlaskForm):
    name = StringField("项目名：", validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField("保存")


class AddTask(FlaskForm):
    task = StringField(
        "任务：",
        validators=[DataRequired(), Length(1, 64)],
        render_kw={"style": "width:40%;", "class": "form-control"},
    )
    title = SelectField(
        "标签：", coerce=int, render_kw={"style": "width:40%;", "class": "form-control"}
    )
    new_title = StringField(
        "新标签：", render_kw={"style": "width:40%;", "class": "form-control"}
    )
    project = SelectField(
        "项目:", render_kw={"style": "width:40%;", "class": "form-control"}
    )
    timenode = StringField(
        "时间节点：",
        render_kw={"style": "width:40%;", "class": "form-control"},
    )
    priority = SelectField(
        "优先级：",
        choices=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4")],
        render_kw={"style": "width:20%;", "class": "form-control"},
    )
    submit = SubmitField(
        "保存",
        render_kw={"class": "btn btn-primary"}
    )

    def __init__(self, *args, **kwargs):
        super(AddTask, self).__init__(*args, **kwargs)
        self.project.choices = [(p.name, p.name) for p in current_user.projects]
        self.title.choices = [(t.id, t.title) for t in current_user.titles]


class Search(FlaskForm):
    s = StringField("", validators=[Required(), Length(1, 64)], id="search")
    search = SubmitField("提交")
