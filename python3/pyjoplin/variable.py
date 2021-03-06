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
    '# double-click: open in prev window',
    '# <CR>: open in prev window',
    '# o: open in prev window',
    '# t: open in new tab',
    '# i: open split',
    '# s: open vsplit',
    '# ct: switch between note and todo type',
    '# cc: switch todo completed',
    '# ',
    '# ' + (options.window_width - 2) * '-',
    '# Notebook node mappings~',
    '# double-click: open & close notebook',
    '# <CR>: open & close notebook',
    '# o: open & close notebook',
    '# O: recursively open notebook',
    '# x: close parent of node',
    '# X: close all child notebooks of current notebook recursively',
    '# r: refresh current notebook',
    '# R: refresh current root',
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
    '# rn: rename a node',
    '# q: close the tree.joplin window',
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
    'ct': 'cmd_ct',
    'cc': 'cmd_cc',
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
    'rn': 'cmd_rn',
}

win_mapping = {
    'ab': 'cmd_ab',
    'q': 'cmd_q',
    '?': 'cmd_question_mark',
}

vmap = {
    'cc': 'vmap_cc',
    'ct': 'vmap_ct',
    'dd': 'vmap_dd',
    'mv': 'vmap_mv',
}

unmap = ['<C-r>', 'u', 'U', 'I', 'a', 'A', 's', 'S', 'd', 'D', 'c', 'C']

info_popup_guide = "*press 'q' to close the window*"
