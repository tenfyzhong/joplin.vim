#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import options


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
    '# ab: add a notebook',
    '# an: add a note',
    '# at: add a todo',
    '# dd: delete a node',
    '# cp: copy a node',
    '# mv: move a node',
    '# q: close the Joplin window',
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
    'dd': 'cmd_dd',
    'mv': 'cmd_mv',
    'cp': 'cmd_cp',
    'an': 'cmd_an',
    'at': 'cmd_at',
}

win_mapping = {
    'ab': 'cmd_ab',
    'q': 'cmd_q',
    '?': 'cmd_question_mark',
}

unmap = ['<C-r>', 'u', 'U', 'I', 'a', 'A', 's', 'S', 'd', 'D', 'c', 'C']

info_popup_guide = "*press 'q' to close the window*"
