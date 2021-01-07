#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import joplin
import tree
import os
import sys

_treenodes = None
_show_help = False
_saved_winnr = -1
_saved_pos = None

width = 30

token = os.environ.get('JOPLIN_TOKEN', '')
if token == '':
    print('JOPLIN_TOKEN is empty')
    sys.exit(-1)

j = joplin.Joplin(token)

_help_lines = [
    '# Joplin quickhelp',
    '# ' + (width - 2) * '='
    '# Note node mappings~',
    '# doublick-click: open in prev window',
    '# <CR>: open in prev window',
    '# o: open in prev window',
    '# t: open in new tab',
    '# i: open split',
    '# s: open vsplit',
    '#',
    '# ' + (width - 2) * '-',
    '# Notebook node mappings~',
    '# double-click: open & close node',
    '# <CR>: open & close node',
    '# o: open & close node',
    '# O: recursively open node',
    '# x: close parent of node',
    '# X: close all child nodes of current node recursively',
    '#',
    '# ' + (width - 2) * '-',
    '# Tree navigation mappings~'
    '# P: go to root',
    '# p: go to parent',
    '# K: go to first child',
    '# J: goto last child',
    '# <C-j>: go to next sibling',
    '# <C-k>: go to prev sibling',
    '#',
    '# ' + (width - 2) * '-',
    '# Other mappings~',
    '# q: Close the Joplin window',
    '# ?: toggle help',
    '# ' + (width - 2) * '=',
    '',
]


def open_window():
    """TODO: Docstring for new_window.
    :returns: TODO

    """
    global _saved_winnr
    global _saved_pos
    _saved_winnr = int(vim.eval('winnr("#")'))
    _saved_pos = vim.eval('getcurpos()')
    bufname = _bufname()
    winnr = vim.eval('bufwinnr("%s")' % bufname)
    winnr = int(winnr)
    if winnr != -1:
        vim.command('win_gotoid("%s")' % winnr)
        return
    vim.command('silent keepalt topleft vertical %d split %s' %
                (width, bufname))
    set_options()
    set_map()
    render()


def set_options():
    vim.current.buffer.options['bufhidden'] = 'hide'
    vim.current.buffer.options['buftype'] = 'nofile'
    vim.current.buffer.options['swapfile'] = False
    vim.current.buffer.options['filetype'] = 'joplin'
    vim.current.buffer.options['modifiable'] = False
    vim.current.buffer.options['readonly'] = False
    vim.current.buffer.options['buflisted'] = False
    vim.current.buffer.options['textwidth'] = 0
    vim.current.window.options['signcolumn'] = 'no'
    vim.current.window.options['winfixwidth'] = True
    vim.current.window.options['foldcolumn'] = 0
    vim.current.window.options['foldmethod'] = 'manual'
    vim.current.window.options['foldenable'] = False
    vim.current.window.options['list'] = False
    vim.current.window.options['spell'] = False
    vim.current.window.options['wrap'] = False
    vim.current.window.options['number'] = True
    vim.current.window.options['relativenumber'] = False
    vim.current.window.options['cursorline'] = True


_mapping_dict = {
    'o': 'cmd_o',
    '<cr>': 'cmd_o',
    '<2-LeftMouse>': 'cmd_o',
    't': 'cmd_t',
    'T': 'cmd_T',
    'i': 'cmd_i',
    's': 'cmd_s',
    'O': 'cmd_O',
    'x': 'cmd_x',
    'X': 'cmd_X',
    'P': 'cmd_P',
    'p': 'cmd_p',
    'K': 'cmd_K',
    'J': 'cmd_J',
    '<C-j>': 'cmd_ctrl_j',
    '<C-k>': 'cmd_ctrl_k',
    'q': 'cmd_q',
    '?': 'cmd_question_mark',
}


def set_map():
    for lhs, rhs in _mapping_dict.items():
        cmd = 'nnoremap <script><silent><buffer>%s <esc>:<c-u>pythonx jplvim.%s()<cr>' % (
            lhs, rhs)
        vim.command(cmd)


def _bufname():
    return 'joplin.tree'


def help_len():
    return len(_help_lines) if has_help() else 0


def render():
    global _treenodes
    global _lines
    if _treenodes is None:
        _treenodes = tree.construct_folder_tree(j)
    lines = note_text(_treenodes, 0)
    helptext = _help_lines if has_help() else []
    cur = list([line.text() for line in lines])
    vim.current.buffer.options['modifiable'] = True
    vim.current.buffer[:] = helptext + cur
    vim.current.buffer.options['modifiable'] = False
    helplen = help_len()
    for i, line in enumerate(lines):
        line.lineno = helplen + i + 1


def note_text(nodes, indent):
    lines = []
    for node in nodes:
        node.indent = indent
        lines.append(node)
        if node.is_open():
            sub = note_text(node.children, indent + 1)
            lines += sub
    return lines


def has_help():
    return vim.current.buffer.vars.get('joplin_help', False)


def get_cur_line():
    base_line = len(_help_lines) if has_help() else 0
    lineno = int(vim.eval('line(".")')) - base_line
    return find_treenode(_treenodes, lineno)


def find_treenode(nodes, lineno):
    i = 0
    j = len(nodes) - 1

    if i > j:
        return None
    if nodes[j].lineno < lineno:
        return find_treenode(nodes[j].children,
                             lineno) if nodes[j].is_folder() else None
    while i <= j:
        mid = int((i + j) / 2)
        if nodes[mid].lineno == lineno:
            return nodes[mid]
        elif nodes[mid].lineno < lineno:
            i = mid + 1
        elif nodes[mid].lineno > lineno:
            j = mid - 1

    mid = i if nodes[i].lineno < lineno else i - 1
    return find_treenode(nodes[mid].children,
                         lineno) if nodes[i].is_folder() else None


def edit(command, treenode):
    lazyredraw_saved = vim.options['lazyredraw']
    dirname = vim.eval('tempname()')
    os.mkdir(dirname)
    filename = dirname + '/' + treenode.node.title + '.md'
    vim.command('silent %s %s' % (command, filename))
    vim.current.buffer.vars['joplin_note_id'] = treenode.node.id
    treenode.fetch(j)
    vim.current.buffer[:] = treenode.node.body.split('\n')
    vim.command('silent noautocmd w')
    vim.options['lazyredraw'] = lazyredraw_saved


def go_to_previous_win():
    if _saved_winnr > 0:
        vim.command('%dwincmd w' % _saved_winnr)
    else:
        vim.command('wincmd w')


def cursor(treenode):
    if treenode.lineno > 0:
        vim.Function('cursor')(treenode.lineno, 1)


def cmd_o():
    global _saved_winnr
    treenode = get_cur_line()
    if treenode is None:
        return
    if treenode.is_folder():
        if treenode.is_open():
            treenode.close()
        else:
            treenode.open(j)
        saved_pos = vim.eval('getcurpos()')
        render()
        vim.Function('setpos')('.', saved_pos)
    else:
        go_to_previous_win()
        edit('edit', treenode)


def cmd_t():
    treenode = get_cur_line()
    if treenode is None:
        return

    if treenode.is_folder():
        edit('tabnew', treenode)


def cmd_i():
    treenode = get_cur_line()
    if treenode is None:
        return
    if not treenode.is_folder():
        go_to_previous_win()
        edit('split', treenode)


def cmd_s():
    treenode = get_cur_line()
    if treenode is None:
        return
    if not treenode.is_folder():
        go_to_previous_win()
        edit('vsplit', treenode)


def open_recusively(treenode):
    if treenode.is_folder() and not treenode.is_open():
        treenode.open(j)

    for child in treenode.children:
        open_recusively(child)


def cmd_O():
    treenode = get_cur_line()
    if treenode is None:
        return
    if treenode.is_folder():
        open_recusively(treenode)
        render()


def cmd_x():
    treenode = get_cur_line()
    if treenode is None:
        return
    treenode = treenode if \
        treenode.is_folder() and treenode.is_open() else \
        treenode.parent
    while treenode is not None and not treenode.is_folder():
        treenode = treenode.parent

    if treenode is not None:
        treenode.close()
        render()
        cursor(treenode)


def close_recurisive(node):
    if not node.is_folder() or not node.is_open():
        return

    node.close()
    for child in node.children:
        close_recurisive(child)


def cmd_X():
    treenode = get_cur_line()
    if not treenode.is_folder():
        return
    close_recurisive(treenode)
    render()
    cursor(treenode)


def cmd_P():
    treenode = get_cur_line()
    while treenode.parent is not None:
        treenode = treenode.parent
    cursor(treenode)


def cmd_p():
    treenode = get_cur_line()
    treenode = treenode.parent if treenode.parent is not None else treenode
    cursor(treenode)


def cmd_K():
    treenode = get_cur_line()
    nodes = treenode.parent.children if \
        treenode.parent is not None else \
        _treenodes
    i = 0
    while i < len(nodes):
        if nodes[i] == treenode:
            break
        i += 1

    if i - 1 >= 0:
        cursor(nodes[i - 1])


def cmd_J():
    pass


def cmd_ctrl_j():
    pass


def cmd_ctrl_k():
    pass


def cmd_q():
    pass


def cmd_question_mark():
    joplin_help = has_help()
    vim.current.buffer.vars['joplin_help'] = not joplin_help
    render()
