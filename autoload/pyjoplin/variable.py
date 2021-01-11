#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import joplin, options, tree

_j = None
_root = None


def get_joplin():
    global _j
    if _j is None:
        if options.token == '':
            vim.command('echo "Joplin: g:joplin_token is empty"')
            return None

        j = joplin.Joplin(options.token, options.host, options.port)
        if j is None:
            vim.command('echo "Joplin: can not create joplin instance"')
            return None
        if not j.ping():
            vim.command('echo "Joplin: can not create joplin instance"')
            return None

        _j = j
    return _j


def get_root():
    global _root
    if _root is None:
        j = get_joplin()
        if j is None:
            return None
        _root = tree.construct_root(j, options.folder_order_by,
                                    options.folder_order_desc)

    return _root


def delete_node_in_list(nodes, id):
    if nodes is None or id == '':
        return nodes

    return list(filter(lambda node: node.node.id != id, nodes))


def del_child(root, id):
    root.children = delete_node_in_list(root.children, id)


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
    '# a: add node',
    '# dd: delete a node',
    '# cp: copy a node',
    '# mv: move a node',
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
    'dd': 'cmd_dd',
    'mv': 'cmd_mv',
    'cp': 'cmd_cp',
}

win_mapping = {
    'a': 'cmd_a',
    'q': 'cmd_q',
    '?': 'cmd_question_mark',
}

unmap = ['<C-r>', 'u', 'U', 'I', 'a', 'A', 's', 'S', 'd', 'D', 'c', 'C']

info_popup_guide = "*press 'q' to close the window*"
menu_popup_guide = "Use j:<down>/k:<up>/q:<quit>/enter,space:<select>,"\
    " or the shortcuts indicated"
