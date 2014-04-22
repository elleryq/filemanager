# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, redirect, request, url_for, flash
from filesystem import Folder, File
from action import *
from flask import request
from os import error
from flask.ext.bootstrap import Bootstrap
from flask.ext.script import Manager
from werkzeug import secure_filename
from flask.logging import create_logger
from shutil import move


UPLOAD_FOLDER = '/tmp'

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    FILES_ROOT=os.path.dirname(os.path.abspath(__file__)),
    UPLOAD_FOLDER=UPLOAD_FOLDER,
    SECRET_KEY='THIS IS AN INSECURE SECRET',
)
bootstrap = Bootstrap(app)
manager = Manager(app)
logger = create_logger(app)


@app.route('/')
@app.route('/files/<path:path>')
def index(path=''):
    path_join = os.path.join(app.config['FILES_ROOT'], path)
    if os.path.isdir(path_join):
        try:
            folders_page = int(request.args.get('folders_page', 1))
        except ValueError:
            folders_page = 1
        try:
            files_page = int(request.args.get('files_page', 1))
        except ValueError:
            files_page = 1
        folder = Folder(app.config['FILES_ROOT'], path)
        folder.read()
        # return render_template('folder.html', folder=folder)
        return render_template('single.html', folder=folder)
    else:
        my_file = File(app.config['FILES_ROOT'], path)
        context = my_file.apply_action(View)
        folder = Folder(app.config['FILES_ROOT'], my_file.get_path())
        if context is None:
            return render_template('file_unreadable.html', folder=folder)
        return render_template('file_view.html',
                               text=context['text'],
                               file=my_file,
                               folder=folder)


@app.route('/search', methods=['POST'])
def search():
    q = request.form['q']
    return render_template('search.html', request=q)


@app.route('/new_directory', methods=["POST"])
@app.route('/<path:path>/new_directory', methods=["POST"])
def create_directory(path="/"):
    dirname = request.form["new_directory_name"]
    directory_root = request.form["directory_root"]
    full_path = os.path.join(directory_root, dirname)
    try:
        os.mkdir(full_path)
    except error:
        pass
    return redirect('/files/' + directory_root)


@app.route('/upload', methods=["GET", "POST"])
def upload():
    if request.method == 'POST':
        location = request.form.get("directory_root", "")
        if location:
            # TODO: Need to check.
            pass
        else:
            location = app.config['FILES_ROOT']

        uploaded_files = request.files.getlist("file[]")
        filenames = []
        for f in uploaded_files:
            if f:
                logger.debug(os.path.basename(f.filename))
                filename = secure_filename(f.filename)
                temporary_path = os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename)
                f.save(temporary_path)

                actual_path = os.path.join(
                    location,
                    os.path.basename(f.filename))
                # TODO: consider if actual_path is existed.
                move(temporary_path, actual_path)

                filenames.append(filename)
        flash("Files are saved.")
        return redirect(url_for('index'))
    return render_template('upload.html')


if __name__ == '__main__':
    manager.run()
