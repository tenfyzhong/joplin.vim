#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import options
from . import joplin
from . import tree

_j = None
_treenodes = None


def get_joplin():
    global _j
    if _j is None:
        if options.token == '':
            print('Joplin: g:joplin_token is empty')
            return None

        j = joplin.Joplin(options.token, options.host, options.port)
        if j is None:
            print('Joplin: can not create joplin instance')
            return None
        if not j.ping():
            print('Joplin: can not create joplin instance')
            return None

        _j = j
    return _j


def root_treenodes():
    global _treenodes
    if _treenodes is None:
        j = get_joplin()
        if j is None:
            return []
        _treenodes = tree.construct_folder_tree(j, options.folder_order_by,
                                                options.folder_order_desc)
    return _treenodes


def bufname():
    return 'tree.joplin'


window_title = [
    int((options.window_width - 11) / 2) * '=' + ' Joplin ' + int(
        (options.window_width - 11) / 2) * '=',
]

help_lines = [
    '# Joplin quickhelp~',
    '# ' + (options.window_width - 2) * '=',
    '# Note node mappings~',
    '# doublick-click: open in prev window',
    '# <CR>: open in prev window',
    '# o: open in prev window',
    '# t: open in new tab',
    '# i: open split',
    '# s: open vsplit',
    '# ',
    '# ' + (options.window_width - 2) * '-',
    '# Notebook node mappings~',
    '# double-click: open & close node',
    '# <CR>: open & close node',
    '# o: open & close node',
    '# O: recursively open node',
    '# x: close parent of node',
    '# X: close all child nodes of current node recursively',
    '# r: refresh cursor folder',
    '# R: refresh cursor root',
    '# ',
    '# ' + (options.window_width - 2) * '-',
    '# Tree navigation mappings~',
    '# P: go to root',
    '# p: go to parent',
    '# K: go to first child',
    '# J: go to last child',
    '# <C-j>: go to next sibling',
    '# <C-k>: go to prev sibling',
    '# ',
    '# ' + (options.window_width - 2) * '-',
    '# Other mappings~',
    '# m: show menu',
    '# q: Close the Joplin window',
    '# ?: toggle help',
    '',
]

treenode_mapping = {
    'o': 'cmd_o',
    '<cr>': 'cmd_o',
    '<2-LeftMouse>': 'cmd_o',
    't': 'cmd_t',
    'i': 'cmd_i',
    's': 'cmd_s',
    'O': 'cmd_O',
    'x': 'cmd_x',
    'X': 'cmd_X',
    'r': 'cmd_r',
    'R': 'cmd_R',
    'P': 'cmd_P',
    'p': 'cmd_p',
    'K': 'cmd_K',
    'J': 'cmd_J',
    '<C-j>': 'cmd_ctrl_j',
    '<C-k>': 'cmd_ctrl_k',
}

win_mapping = {
    'm': 'cmd_m',
    'q': 'cmd_q',
    '?': 'cmd_question_mark',
}

unmap = ['<C-r>', 'u', 'U', 'I', 'a', 'A', 's', 'S', 'd', 'D', 'c', 'C']
