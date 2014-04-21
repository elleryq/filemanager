# -*- coding: utf-8 -*-
from genericpath import isfile
import os
from os.path import join, basename, splitext, isdir, dirname
from action import View
import string


class PaginationList(list):
    def get_page(self, page=1, per_page=10):
        if page < 1:
            raise Exception("Spcified page is not existed.")
        start = (page-1)*per_page

        count = len(self)
        end = page*per_page
        if start > count:
            raise Exception("Spcified page is not existed.")
        if end > count:
            end = count
        return self[start:end]


class Node(object):
    def __init__(self, root, path):
        splitetPath = string.split(path, "/")
        self.path = os.path.sep.join(splitetPath)
        self.root = root
        self._basename = basename(self.path)

    def __unicode__(self):
        return self.name

    def get_actions(self):
        return self.avaliable_actions

    def apply_action(self, action_class):
        action = action_class(self)
        return action.apply()

    def isdir(self):
        return isdir(join(self.root, self.path))

    def isfile(self):
        return isfile(join(self.root, self.path))

    def key(self):
        if self.isdir():
            t = 'D'
        elif self.isfile():
            t = 'F'
        else:
            t = ' '
        return '{0}{1}'.format(t, self.name)


class File(Node):
    avaliable_actions = [View, ]

    def __unicode__(self):
        return self.name

    @property
    def extension(self):
        return splitext(self._basename)[1]

    @property
    def name(self):
        return self._basename

    def get_path(self):
        return dirname(self.path)


class Folder(Node):

    def __init__(self, root, path):
        super(Folder, self).__init__(root, path)
        # self.files = []
        # self.folders = []
        self.files = PaginationList()
        self.folders = PaginationList()
        self.nodes = PaginationList()

    @property
    def name(self):
        return basename(self.path)

    def chunks(self):
        chunk_path = ''
        for chunk in self.path.split(os.sep):
            chunk_path = join(chunk_path, chunk)
            yield {'chunk': chunk, 'path': chunk_path}

    def read(self):
        for entry in os.listdir(join(self.root, self.path)):
            full_path = join(self.path, entry)
            if isdir(join(self.root, full_path)):
                node = Folder(self.root, full_path)
                self.folders.append(node)
            if isfile(join(self.root, full_path)):
                node = File(self.root, full_path)
                self.files.append(node)
            self.nodes.append(node)
        self.nodes.sort(key=lambda node: node.key())
