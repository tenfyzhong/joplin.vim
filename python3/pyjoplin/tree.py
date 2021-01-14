#!/usr/bin/env python
# -*- coding: utf-8 -*-

from operator import attrgetter

from .node import FolderNode, NoteNode


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
        return 'isopen,%s:%d:%d:%s' % (self._open, len(
            self.children), self.lineno, str(self.node))

    def __repr__(self):
        return 'isopen,%s:%d:%d:%s' % (self._open, len(
            self.children), self.lineno, str(self.node))

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
        # update folders
        tree_folders = list(
            filter(lambda node: node.is_folder(), self.children))
        svr_folders = joplin.get_all(FolderNode)
        self_svr_folders = list(
            filter(lambda folder: folder.parent_id == self.node.id,
                   svr_folders))
        self_folders_id = set([node.id for node in self_svr_folders])
        tree_folders = list(
            filter(lambda node: node.node.id in self_folders_id, tree_folders))
        cur_folder_ids = set([folder.node.id for folder in tree_folders])

        new_fodlers = list(
            filter(lambda node: node.id not in cur_folder_ids,
                   self_svr_folders))
        new_folder_nodes = list([TreeNode(folder) for folder in new_fodlers])
        tree_folders += new_folder_nodes

        tree_folders = sorted(tree_folders,
                              key=attrgetter('node.' + folder_order_by),
                              reverse=folder_order_desc)
        self.children = tree_folders
        if self.node.id != '':
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
            self.children += tree_notes
        self.fetched = True
        self.dirty = False
        for i, node in enumerate(self.children):
            node.parent = self
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


def construct_root(joplin, order_by, order_desc=False):
    """construct_root of all
    :returns: TreeNode
    """
    # folders
    folders = joplin.get_all(FolderNode)
    folders = sorted(folders, key=attrgetter(order_by), reverse=order_desc)
    nodes = list([TreeNode(folder) for folder in folders])

    root = TreeNode(FolderNode())
    d = dict({node.node.id: node for node in nodes})
    d[''] = root
    for node in nodes:
        parent = d[node.node.parent_id]
        node.parent = parent
        node.parent.children.append(node)

    nodes = list([node for node in nodes if node.parent == root])
    for i, node in enumerate(nodes):
        node.child_index_of_parent = i
    root.children = nodes
    root._open = True
    root.fetched = True
    return root


def node_path(node):
    if node is None or node.node is None:
        return ''
    p = node
    path = []
    while p is not None and p.node is not None and p.node.title != '':
        path.append(p.node.title)
        p = p.parent

    path = reversed(path)
    return '/'.join(path)
