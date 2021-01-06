#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import joplin
import tree
import os
from node import NoteNode

_treenodes = None
_lines = None
_show_help = False
_base_line = 0

_saved_winnr = -1
_saved_pos = None

width = 30

token = os.environ.get('JOPLIN_TOKEN', '')
if token == '':
    print('JOPLIN_TOKEN is empty')
    os.exit(-1)

j = joplin.Joplin(token)

_help_lines = [
    '# Joplin quickhelp',
    '# ' + (width - 2) * '='
    '# Note node mappings~',
    '# doublick-click: open in prev window',
    '# <CR>: open in prev window',
    '# o: open in prev window',
    '# t: open in new tab',
    '# T: open in new tab silent',
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
    '',
    '# ' + (width - 2) * '-',
]


class Line(object):
    """Docstring for Line. """
    def __init__(self, treenode, indent):
        """TODO: to be defined.

        :treenode: TODO

        """
        self.treenode = treenode
        self._indent = indent

    def text(self):
        """TODO: Docstring for text.
        :returns: TODO

        """
        sign = ''
        if not self.treenode.is_folder():
            sign = '  '
        else:
            sign = '- ' if self.treenode.is_open() else '+ '
        line = self._indent * '  ' + sign + self.treenode.node.title
        return line


def open_window():
    """TODO: Docstring for new_window.
    :returns: TODO

    """
    global _saved_winnr
    global _saved_pos
    _saved_winnr = int(vim.eval('bufwinnr("%")'))
    _saved_pos = vim.eval('getcurpos("%")')
    bufname = _bufname()
    winnr = vim.eval('bufwinnr("%s")' % bufname)
    winnr = int(winnr)
    if winnr != -1:
        print('wtf')
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


def help():
    return _help_lines if _show_help else []


def render():
    global _treenodes
    global _lines
    global _base_line
    if _treenodes is None:
        _treenodes = tree.construct_folder_tree(j)
    lines = note_text(_treenodes, 0)
    text = help()
    _base_line = len(text)
    text += list([line.text() for line in lines])
    vim.current.buffer.options['modifiable'] = True
    vim.current.buffer[:] = text
    vim.current.buffer.options['modifiable'] = False
    _lines = lines


def note_text(nodes, indent):
    lines = []
    for node in nodes:
        line = Line(node, indent)
        lines.append(line)
        if node.is_open():
            sub = note_text(node.children, indent + 1)
            lines += sub
    return lines


def cmd_o():
    global _lines
    global _saved_winnr
    lineno = int(vim.eval('line(".")')) - _base_line
    if lineno > len(_lines):
        print('illegal lineno %d' % lineno)
        return

    line = _lines[lineno - 1]
    if line.treenode.is_folder():
        if not line.treenode.fetched or line.treenode.dirty:
            line.treenode.fetch(j)

        if line.treenode.is_open():
            line.treenode.close()
        else:
            line.treenode.open()
        saved_pos = vim.eval('getcurpos()')
        render()
        vim.Function('setpos')('.', saved_pos)
    else:
        if _saved_winnr > 0:
            vim.command('wincmd w')
        else:
            vim.command('%dwincmd w' % _saved_winnr)

        dirname = vim.eval('tempname()')
        os.mkdir(dirname)
        filename = dirname + '/' + line.treenode.node.title
        vim.command('e ' + filename)
        vim.current.buffer.options['filetype'] = 'markdown'
        note = j.get(NoteNode, line.treenode.node.id)
        vim.current.buffer[:] = note.body.split('\n')


def cmd_t():
    pass


def cmd_T():
    pass


def cmd_i():
    pass


def cmd_s():
    pass


def cmd_O():
    pass


def cmd_x():
    pass


def cmd_X():
    pass


def cmd_P():
    pass


def cmd_p():
    pass


def cmd_K():
    pass


def cmd_J():
    pass


def cmd_ctrl_j():
    pass


def cmd_ctrl_k():
    pass


def cmd_q():
    pass


def cmd_question_mark():
    pass