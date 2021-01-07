#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import os

# from joplin import Joplin
from node import FolderNode, NoteNode


class TreeNode(object):
    """TreeNode"""
    def __init__(self, node=None):
        self.parent = None
        self.node = node
        self.children = []
        self.fetched = False
        self.dirty = False
        self._open = False
        self.lineno = 0
        self.indent = 0
        self.child_index_of_parent = -1

    def __str__(self):
        return str(self.node)

    def __repr__(self):
        return str(self.node)

    def text(self, iconopen, iconclose, iconnote, icontodo, iconcompleted):
        sign = ''
        if not self.is_folder():
            sign = '  '
            if self.node.is_todo:
                sign += iconcompleted if self.node.todo_completed else icontodo
            else:
                sign += iconnote
        else:
            sign = iconopen if self.is_open() else iconclose
            sign += ' '
        line = self.indent * '  ' + sign + self.node.title
        return line

    def open(self, joplin):
        if not self.is_folder():
            return
        self._open = True
        if not self.fetched or self.dirty:
            self.fetch(joplin)

    def close(self):
        if not self.is_folder():
            return
        self._open = False

    def is_open(self):
        return self._open and self.is_folder()

    def is_folder(self):
        return isinstance(self.node, FolderNode)

    def fetch(self, joplin):
        """Fetch all notes from joplin
        :joplin: joplin instance
        """
        if self.is_folder():
            # remove notes
            self.children = list([
                node for node in self.children
                if isinstance(node.node, FolderNode)
            ])
            notes = joplin.get_folder_notes(self.node.id)
            nodes = list([TreeNode(note) for note in notes])
            for node in nodes:
                node.parent = self
            self.children += nodes
            self.fetched = True
            self.dirty = False
            for i, node in enumerate(self.children):
                node.child_index_of_parent = i
        else:
            note = joplin.get(NoteNode, self.node.id)
            self.node = note

    def prop_type(self):
        if self.is_folder():
            return 'joplin_folder'
        elif self.node.is_todo:
            return 'joplin_completed' if \
                self.node.todo_completed else \
                'joplin_todo'
        else:
            return ''


def construct_folder_tree(joplin):
    """construct folder tree

    :returns: TreeNodes

    """
    # folders
    folders = joplin.get_all(FolderNode)
    nodes = list([TreeNode(folder) for folder in folders])
    d = dict({node.node.id: node for node in nodes})
    for node in nodes:
        if node.node.parent_id != '':
            parent = d[node.node.parent_id]
            node.parent = parent
            node.parent.children.append(node)

    nodes = list([node for node in nodes if node.parent is None])
    for i, node in enumerate(nodes):
        node.child_index_of_parent = i
    return nodes
