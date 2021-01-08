#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import os

# from joplin import Joplin
from .node import FolderNode, NoteNode
from operator import attrgetter


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
            sign = ' '
            if self.node.is_todo:
                sign += iconcompleted if self.node.todo_completed else icontodo
            else:
                sign += iconnote
        else:
            sign = iconopen if self.is_open() else iconclose
        line = self.indent * ' ' + sign + self.node.title
        return line

    def open(self, joplin, pin_todo, hide_completed, folder_order_by,
             folder_order_desc, note_order_by, note_order_desc):
        if not self.is_folder():
            return
        self._open = True
        if not self.fetched or self.dirty:
            self.fetch_folder(joplin, pin_todo, hide_completed,
                              folder_order_by, folder_order_desc,
                              note_order_by, note_order_desc)

    def close(self):
        if not self.is_folder():
            return
        self._open = False

    def is_open(self):
        return self._open and self.is_folder()

    def is_folder(self):
        return isinstance(self.node, FolderNode)

    def fetch_note(self, joplin):
        if self.is_folder():
            return
        note = joplin.get(NoteNode, self.node.id)
        self.node = note

    def fetch_folder(self, joplin, pin_todo, hide_completed, folder_order_by,
                     folder_order_desc, note_order_by, note_order_desc):
        """Fetch all notes from joplin
        :joplin: joplin instance
        """
        if not self.is_folder():
            return
        # remove notes
        tree_folders = list(
            filter(lambda node: node.is_folder(), self.children))
        tree_folders = sorted(tree_folders,
                              key=attrgetter('node.' + folder_order_by),
                              reverse=folder_order_desc)
        todo_notes = joplin.get_folder_notes(self.node.id)
        if hide_completed:
            todo_notes = list(
                filter(
                    lambda node: not node.node.is_todo or not node.
                    todo_completed, todo_notes))
        if pin_todo:
            todos = []
            notes = []
            for node in todo_notes:
                if node.is_todo and not node.todo_completed:
                    todos.append(node)
                else:
                    notes.append(node)
            todos = sorted(todos,
                           key=attrgetter(note_order_by),
                           reverse=note_order_desc)
            notes = sorted(notes,
                           key=attrgetter(note_order_by),
                           reverse=note_order_desc)
            todo_notes = todos + notes
        else:
            todo_notes = sorted(todo_notes,
                                key=attrgetter(note_order_by),
                                reverse=note_order_desc)
        tree_notes = list([TreeNode(note) for note in todo_notes])
        for note in tree_notes:
            note.parent = self
        self.children = tree_folders + tree_notes
        self.fetched = True
        self.dirty = False
        for i, node in enumerate(self.children):
            node.child_index_of_parent = i

    def prop_type(self):
        if self.is_folder():
            return 'joplin_folder'
        elif self.node.is_todo:
            return 'joplin_completed' if \
                self.node.todo_completed else \
                'joplin_todo'
        else:
            return ''


def construct_folder_tree(joplin, order_by, order_desc=False):
    """construct folder tree

    :returns: TreeNodes

    """
    # folders
    folders = joplin.get_all(FolderNode)
    folders = sorted(folders, key=attrgetter(order_by), reverse=order_desc)
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
