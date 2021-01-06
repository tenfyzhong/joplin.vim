#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import os

# from joplin import Joplin
from node import FolderNode


class TreeNode(object):
    """TreeNode"""
    def __init__(self, node=None):
        self.parent = None
        self.node = node
        self.children = []
        self.fetched = False
        self.dirty = False
        self._open = False

    def __str__(self):
        return str(self.node)

    def __repr__(self):
        return str(self.node)

    def fetch(self, joplin):
        """Fetch all notes from joplin
        :joplin: joplin instance
        """
        # remove notes
        self.children = list([
            node for node in self.children
            if isinstance(node.node, FolderNode)
        ])
        notes = joplin.get_folder_notes(self.node.id)
        nodes = list([TreeNode(note) for note in notes])
        self.children += nodes
        self.fetched = True
        self.dirty = False


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

    return list([node for node in nodes if node.parent is None])


# def fetch(joplin, nodes):
#     for node in nodes:
#         fetch(joplin, node.children)
#         node.fetch(joplin)

# def print_nodes(nodes, prefix):
#     for node in nodes:
#         print(prefix, node)
#         print_nodes(node.children, prefix + '--')

# if __name__ == '__main__':
#     token = os.environ['JOPLIN_TOKEN']
#     assert token != ''
#     j = Joplin(token)
#     nodes = construct_folder_tree(j)
#     fetch(j, nodes)
#     print_nodes(nodes, '')
