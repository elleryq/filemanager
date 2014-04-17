# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, redirect, request
from filesystem import Folder, File
from action import *
from flask import request
from os import error
from celery import Celery

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


app = Flask(__name__)
app.config.update(
    DEBUG=True,
    FILES_ROOT=os.path.dirname(os.path.abspath(__file__)),
    CELERY_BROKER_URL='sqla+sqlite:///celerydb.sqlite',
    CELERY_RESULT_BACKEND='db+sqlite:///results.sqlite',
)
celery = make_celery(app)


@celery.task()
def copy_log(src, dst):
    # TODO: need long time.
    return True


@app.route('/')
@app.route('/files/<path:path>')
def index(path=''):
    path_join = os.path.join(app.config['FILES_ROOT'], path)
    if os.path.isdir(path_join):
        folder = Folder(app.config['FILES_ROOT'], path)
        folder.read()
        return render_template('folder.html', folder=folder)
    else:
        my_file = File(app.config['FILES_ROOT'], path)
        context = my_file.apply_action(View)
        folder = Folder(app.config['FILES_ROOT'], my_file.get_path())
        if context == None:
            return render_template('file_unreadable.html', folder=folder)
        return render_template('file_view.html', text=context['text'], file=my_file, folder=folder)

@app.route('/search', methods=['POST'])
def search():
    q = request.form['q']
    return render_template('search.html', request = q)

@app.route('/new_directory', methods=["POST"])
@app.route('/<path:path>/new_directory', methods=["POST"])
def create_directory(path = "/"):
    dirname = request.form["new_directory_name"]
    directory_root = request.form["directory_root"]
    full_path = os.path.join(directory_root, dirname)
    try:
        os.mkdir(full_path)
    except error:
        pass
    return redirect('/files/' + directory_root)
    


if __name__ == '__main__':
    app.run(host="0.0.0.0")
