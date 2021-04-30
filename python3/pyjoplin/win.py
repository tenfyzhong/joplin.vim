#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import tempfile
import time
from datetime import datetime

import vim

from . import joplin, options, tree, variable
from .node import FolderNode, NoteNode, ResourceNode, TagNode
from .variable import bufname

props = {
    'joplin_folder': 'Identifier',
    'joplin_todo': 'Todo',
    'joplin_completed': 'Comment',
    'joplin_help_title': 'Define',
    'joplin_window_title': 'Constant',
    'joplin_help_keyword': 'Identifier',
    'joplin_help_summary': 'String',
    'joplin_help_sperate': 'String',
    'joplin_help_prefix': 'String',
    'joplin_popup_info_tag': 'Statement',
    'joplin_popup_guide': 'Comment',
}

for name, highlight in props.items():
    vim.Function('prop_type_add')(name, {'highlight': highlight})


def prop_add(nr, prop_type, col_begin=1, col_end=0):
    if prop_type == '':
        return
    vim.Function('cursor')(nr, 1)
    if col_end == 0:
        col_end = vim.Function('col')('$')
    vim.Function('prop_add')(nr, col_begin, {
        'end_col': col_end,
        'type': prop_type,
    })


class Win(object):
    def __init__(self):
        self._joplin = None
        self._root = None
        self._last_query = None
        self._has_help = False
        self._inited = False
        self._basedir = tempfile.mkdtemp()

        base = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        self._info_dir = os.path.join(base, '.info')

    def health(self):
        return self._joplin and self._joplin.ping()

    def init(self):
        if self._inited:
            return
        self._joplin = joplin.Joplin(options.token, options.host, options.port)
        if not self._joplin.ping():
            return
        self._root = tree.construct_root(self._joplin, options.folder_order_by,
                                         options.folder_order_desc)

        self._inited = True

    def open(self):
        """open joplin window
        """
        bufname_ = bufname()
        winnr = vim.Function('bufwinnr')(bufname_)
        if winnr != -1:
            vim.command('%dwincmd w' % winnr)
            return
        vim.command('silent keepalt topleft vertical %d split %s' %
                    (options.window_width, bufname_))
        set_options()
        set_map()
        self._render()
        last_line = vim.current.buffer.vars.get('saved_last_line',
                                                len(variable.window_title) + 1)
        vim.Function('cursor')(last_line, 1)

    def close(self):
        bufname_ = bufname()
        winnr = vim.Function('bufwinnr')(bufname_)
        if winnr > 0:
            vim.command('%dclose' % winnr)

    def toggle(self):
        if vim.Function('bufwinnr')(bufname()) > 0:
            self.close()
        else:
            self.open()

    def write(self):
        note_id = vim.current.buffer.vars.get('joplin_note_id', b'').decode()
        if note_id == '':
            return

        note = self._joplin.get(NoteNode, note_id)
        if note is None:
            return

        body = '\n'.join(vim.current.buffer[:])

        in_diff = vim.current.buffer.vars.get('joplin_diff', False)

        updated_time = vim.current.buffer.vars['joplin_updated']
        if not in_diff and \
                note.updated_time > updated_time and \
                note.body != body:
            select = 0
            prompt = '<%s> has a newer version, update time %s, (D)iff, '\
                '(o)verwrite: ' % (note.title, strftime(note.updated_time))
            vim.command('echo "Joplin: %s"' % prompt)
            select = 0
            while True:
                select = vim.Function('getchar')()
                if select in [68, 100, 13, 27]:
                    # D, d, <cr>, <esc>
                    self._diff(note)
                    return
                elif select in [79, 111]:
                    # O, o
                    break

        note.body = body
        note = self._joplin.put(note)
        if note is None:
            return
        vim.current.buffer.vars['joplin_updated'] = note.updated_time
        # remove unless diff buffer
        if not in_diff:
            diffnr = vim.current.buffer.vars.get('diffnr', [])
            prog = re.compile(note.title + r'\.remote\.\d*\.md')
            for bufnr in diffnr:
                bufname = vim.Function('bufname')(bufnr).decode()
                basename = os.path.basename(bufname)
                if prog.match(basename):
                    vim.command('%dbdelete!' % bufnr)

            vim.current.buffer.vars['diffnr'] = []

        vim.command('noautocmd w')
        vim.command('set nomodified')

    def leave(self):
        note_id = vim.current.buffer.vars.get('joplin_note_id', b'').decode()
        if note_id != '':
            self._save_pos(note_id)

    def diffleave(self, id):
        vim.command('wincmd w')
        vim.current.buffer.vars['joplin_diff'] = False
        vim.current.buffer.vars['joplin_updated'] = int(time.time() * 1000)
        vim.command('diffoff')
        vim.command('wincmd w')

    def saveas(self, is_todo, path):
        folders = path.split('/')
        parent = self._find_folder_by_path(folders)
        if parent is None:
            vim.command('echo "Joplin: not such notebook<%s>"' % path)
            return

        if parent.node.id == '':
            vim.command('echo "Joplin: note should copy to a notebook"')
            return

        new_title = vim.Function('expand')('%:p:t').decode()
        note = NoteNode()
        body = '\n'.join(vim.current.buffer[:])
        note.parent_id = parent.node.id
        note.title = new_title
        note.body = body
        note.is_todo = is_todo
        note = self._joplin.post(note)
        if note is None:
            vim.command('echo "Joplin: New note failed"')
            return
        self._refresh_render(parent)
        note_local_setting()
        vim.current.buffer.vars['joplin_note_id'] = note.id
        vim.command('noautocmd w')

    def _diff(self, note):
        newfile = os.path.join(
            self._basedir, note.id,
            '%s.remote.%d.md' % (note.title, note.updated_time))
        with open(newfile, 'w') as f:
            f.write(note.body)

        vim.command('only')
        vim.current.buffer.vars['joplin_diff'] = True
        vim.command('diffsplit %s' % newfile)
        bufnr = vim.Function('bufnr')()
        vim.command('autocmd BufWinLeave <buffer> python3 '
                    'pyjoplin.win.diffleave("%s")' % note.id)
        vim.command('wincmd w')
        # vim.command('set modified')
        diffnr = list(vim.current.buffer.vars.get('diffnr', []))
        diffnr.append(bufnr)
        vim.current.buffer.vars['diffnr'] = diffnr

    def _render_help(self, nr):
        lines = variable.help_lines if self._has_help else []
        for text in lines:
            vim.current.buffer.append(text, nr)
            prop_add(nr + 1, 'joplin_help_prefix', 1, 3)
            if re.match(r'^# =+$|^# -+$', text):
                prop_add(nr + 1, 'joplin_help_sperate', 3)
            elif re.match(r'^# .*~$', text):
                prop_add(nr + 1, 'joplin_help_title', 3)
            elif re.match(r'^# [^:]*:.*$', text):
                vim.Function('cursor')(nr + 1, 1)
                vim.command('noautocmd normal f:')
                col = vim.Function('col')('.')
                prop_add(nr + 1, 'joplin_help_keyword', 3, col)
                prop_add(nr + 1, 'joplin_help_summary', col)
            nr += 1
        return nr

    def _render_title(self, nr):
        for text in variable.window_title:
            vim.current.buffer.append(text, nr)
            prop_add(nr + 1, 'joplin_window_title')
            nr += 1
        return nr

    def _render_nodes(self, nr):
        root = self._root
        if root is None:
            return nr

        lines = tree_line(root, -1)
        for line in lines:
            vim.current.buffer.append(
                line.text(options.icon_open, options.icon_close,
                          options.icon_note, options.icon_todo,
                          options.icon_completed), nr)
            line.lineno = nr + 1
            prop_type = line.prop_type()
            prop_add(nr + 1, prop_type)
            nr += 1

        return nr

    def _render(self):
        winnr_saved = vim.Function('winnr')()
        winnr = vim.Function('bufwinnr')(bufname())
        if winnr < 0:
            return
        vim.command('%dwincmd w' % winnr)
        vim.current.buffer.options['modifiable'] = True
        del vim.current.buffer[:]
        nr = 0
        nr = self._render_help(nr)
        nr = self._render_title(nr)
        nr = self._render_nodes(nr)
        # delete empty line
        del vim.current.buffer[nr]
        vim.current.buffer.options['modifiable'] = False
        if winnr_saved != winnr:
            vim.command('%dwincmd w' % winnr_saved)

    def _save_pos(self, id):
        path = os.path.join(self._info_dir, id)
        winid = vim.Function('bufwinid')('%')
        wininfo = vim.Function('getwininfo')(winid)
        if len(wininfo) == 0:
            return
        last_cursor = wininfo[0].get('variables',
                                     {}).get('last_cursor', [0, 1, 1, 0, 0])
        lnum = last_cursor[1]
        col = last_cursor[2]
        topline = wininfo[0].get('topline', 1)
        try:
            with open(path, 'w') as f:
                f.write('%d,%d,%d' % (lnum, col, topline))
        except Exception:
            pass

    def _set_pos(self, id):
        path = os.path.join(self._info_dir, id)
        try:
            with open(path) as f:
                line = f.readline()
                items = line.split(',')
                if len(items) < 3:
                    return
                lnum = int(items[0])
                col = int(items[1])
                topline = int(items[2])
                lnum = lnum if lnum > 0 else 1
                col = col if col > 0 else 1
                topline = topline if topline > 0 else lnum

                scrolloff_saved = vim.options['scrolloff']
                vim.options['scrolloff'] = 0
                vim.command('normal! %dzt' % topline)
                vim.options['scrolloff'] = scrolloff_saved

                vim.Function('cursor')(lnum, col)
        except Exception:
            pass

    def _edit_note(self, command, reopen_tree, note, joplin_treenode_line):
        lazyredraw_saved = vim.options['lazyredraw']
        winview_saved = vim.Function('winsaveview')()
        undolevel_saved = vim.options['undolevels']
        vim.options['undolevels'] = -1
        dirname = os.path.join(self._basedir, note.id)
        filename = note.title + '.md'
        filename = filename.replace('/', '-')
        filename = os.path.join(dirname, filename)
        filename = vim.Function('fnameescape')(filename).decode()
        try:
            os.mkdir(dirname)
        except FileExistsError:
            pass
        except Exception as e:
            vim.command('echo "Joplin: can not create <%s>, %s"' %
                        (dirname, e))
            return

        existed = os.path.isfile(filename)
        vim.command('lcd %s' % dirname)
        vim.command('silent %s %s' % (command, filename))
        vim.current.buffer.vars['joplin_note_id'] = note.id
        vim.current.buffer.vars['joplin_path'] = self._joplin.node_path(note)
        vim.current.buffer.vars['joplin_updated'] = note.updated_time
        vim.current.buffer.options['filetype'] = 'joplin.markdown'
        if joplin_treenode_line > 0:
            vim.current.buffer.vars[
                'joplin_treenode_line'] = joplin_treenode_line

        vim.options['lazyredraw'] = True
        if not existed:
            vim.current.buffer[:] = note.body.split('\n')
            vim.command('silent noautocmd w')

        if reopen_tree:
            # check joplin window
            # reopen if not exist
            winnr = vim.Function('bufwinnr')(bufname())
            if winnr < 0:
                note_bufname = vim.Function('bufname')()
                self.open()
                vim.Function('winrestview')(winview_saved)
                winnr = vim.Function('bufwinnr')(note_bufname)
                vim.command('%dwincmd w' % winnr)

        self._set_pos(note.id)
        vim.command('redraw!')
        vim.command('silent call joplin#statusline#refresh()')

        vim.options['lazyredraw'] = lazyredraw_saved
        vim.options['undolevels'] = undolevel_saved
        note_local_setting()

    def edit(self, command, treenode):
        treenode.fetch_note(self._joplin)
        self._edit_note(command, True, treenode.node, treenode.lineno)

    def _refresh_render(self, treenode):
        self._refresh(treenode)
        self._render()

    def _refresh(self, treenode):
        if treenode is None:
            return
        if not treenode.is_folder():
            return
        if not treenode.is_open():
            # if the current node is close
            # not need to refresh current node
            # buf if it has fetch data, sould set to dirty
            # it will fetch data when open
            treenode.dirty = treenode.fetched
            return
        treenode.fetch_folder(self._joplin, options.pin_todo,
                              options.hide_completed, options.folder_order_by,
                              options.folder_order_desc, options.note_order_by,
                              options.note_order_desc)
        for child in treenode.children:
            self._refresh(child)

    # ============================== complete
    def complete_note_tag(self):
        note_id = vim.current.buffer.vars.get('joplin_note_id', b'').decode()
        if note_id == '':
            return ''
        tags = list([tag.title for tag in self._joplin.get_note_tags(note_id)])
        tags = sorted(tags)
        return '\n'.join(tags)

    def complete_resource(self):
        resources = self._joplin.get_all(ResourceNode)
        titles = list([resource.title for resource in resources])
        titles = sorted(list(set(titles)))
        return '\n'.join(titles)

    def complete_tag(self):
        tags = self._joplin.get_all(TagNode)
        titles = list([tag.title for tag in tags])
        titles = sorted(list(set(titles)))
        return '\n'.join(titles)

    def complete_note(self, arg_lead):
        path = arg_lead.split(r'/')
        path = path[:-1]
        root = self._find_folder_by_path(path)
        if root is None:
            return ''
        root.fetch_folder(self._joplin, options.pin_todo,
                          options.hide_completed, options.folder_order_by,
                          options.folder_order_desc, options.note_order_by,
                          options.note_order_desc)
        dirname = tree.node_path(root)
        lines = list(
            [dirname + '/' + node.node.title for node in root.children])
        lines = list(
            map(lambda line: line[1:]
                if line.startswith('/') else line, lines))
        return '\n'.join(lines)

    def complete_folder(self, arg_lead):
        path = arg_lead.split('/')
        path = path[:-1]
        root = self._find_folder_by_path(path)
        if root is None:
            return ''
        dirname = tree.node_path(root)
        lines = list([
            dirname + '/' + node.node.title for node in root.children
            if node.is_folder()
        ])
        lines = list(
            map(lambda line: line[1:]
                if line.startswith('/') else line, lines))
        text = '\n'.join(lines)
        return text

    # ============================== treenode cmd
    def cmd_o(self, treenode):
        if treenode is None:
            return

        if treenode.is_folder():
            if treenode.is_open():
                treenode.close()
            else:
                treenode.open(self._joplin, options.pin_todo,
                              options.hide_completed, options.folder_order_by,
                              options.folder_order_desc, options.note_order_by,
                              options.note_order_desc)
            saved_pos = vim.eval('getcurpos()')
            self._render()
            vim.Function('setpos')('.', saved_pos)
        else:
            go_to_previous_win()
            self.edit('edit', treenode)

    def cmd_t(self, treenode):
        if treenode is None:
            return

        if not treenode.is_folder():
            self.edit('tabnew', treenode)

    def cmd_i(self, treenode):
        if treenode is None:
            return

        if not treenode.is_folder():
            go_to_previous_win()
            self.edit('split', treenode)

    def cmd_s(self, treenode):
        if treenode is None:
            return

        if not treenode.is_folder():
            go_to_previous_win()
            self.edit('vsplit', treenode)

    def cmd_ct(self, treenode):
        if treenode is None:
            return
        if treenode.is_folder():
            return
        self._note_type_switch(treenode.node.id)
        self._refresh_render(treenode.parent)
        cursor(treenode)

    def cmd_cc(self, treenode):
        if treenode is None:
            return
        if treenode.is_folder():
            return
        if not self._todo_completed_switch(treenode.node.id):
            return
        self._refresh_render(treenode.parent)
        cursor(treenode)

    def open_recusively(self, treenode):
        if treenode.is_folder() and not treenode.is_open():
            treenode.open(self._joplin, options.pin_todo,
                          options.hide_completed, options.folder_order_by,
                          options.folder_order_desc, options.note_order_by,
                          options.note_order_desc)

        for child in treenode.children:
            self.open_recusively(child)

    def cmd_O(self, treenode):
        if treenode is None:
            return

        if not treenode.is_folder():
            return
        if treenode.is_open():
            self.close_recurisive(treenode)
        else:
            self.open_recusively(treenode)

        self._render()
        cursor(treenode)

    def cmd_x(self, treenode):
        if treenode is None:
            return

        parent = treenode.parent
        if parent is None or parent.node.id == '' or not parent.is_open():
            return

        parent.close()
        self._render()
        cursor(parent)

    def close_recurisive(self, node):
        if not node.is_folder() or not node.is_open():
            return

        node.close()
        for child in node.children:
            self.close_recurisive(child)

    def cmd_X(self, treenode):
        if treenode is None:
            return

        if not treenode.is_folder():
            return
        self.close_recurisive(treenode)
        self._render()
        cursor(treenode)

    def cmd_r(self, treenode):
        if treenode is None:
            return

        lastnode = treenode
        if not treenode.is_folder():
            treenode = treenode.parent
        self._refresh_render(treenode)
        cursor(lastnode)
        vim.command('echo "Joplin: Refreshed!"')

    def cmd_R(self, treenode):
        if treenode is None:
            return

        lastnode = treenode
        while treenode.parent is not None:
            treenode = treenode.parent
        self._refresh_render(treenode)
        cursor(lastnode)
        vim.command('echo "Joplin: Refreshed!"')

    def cmd_P(self, treenode):
        if treenode is None:
            return

        while treenode.parent.node.id != '':
            treenode = treenode.parent
        cursor(treenode)

    def cmd_p(self, treenode):
        if treenode is None:
            return

        treenode = treenode.parent if \
            treenode.parent.node.id != '' else \
            treenode
        cursor(treenode)

    def cmd_K(self, treenode):
        if treenode is None:
            return

        if len(treenode.parent.children) > 0:
            cursor(treenode.parent.children[0])

    def cmd_J(self, treenode):
        if treenode is None:
            return

        if len(treenode.parent.children) > 0:
            cursor(treenode.parent.children[-1])

    def cmd_ctrl_j(self, treenode):
        if treenode is None:
            return

        nodes = treenode.parent.children
        i = treenode.child_index_of_parent + 1
        if i < len(nodes):
            cursor(nodes[i])

    def cmd_ctrl_k(self, treenode):
        if treenode is None:
            return

        nodes = treenode.parent.children
        i = treenode.child_index_of_parent - 1
        if i >= 0:
            cursor(nodes[i])

    def cmd_q(self):
        self.close()

    def cmd_question_mark(self):
        self._has_help = not self._has_help
        self._render()
        vim.Function('cursor')(1, 1)

    def cmd_ab(self):
        self.cmd_a('Add notebook to path: ', True, 0)

    def cmd_at(self, treenode):
        self.cmd_a('Add todo to path: ', False, 1)

    def cmd_an(self, treenode, **kwargs):
        self.cmd_a('Add note to path: ', False, 0)

    def cmd_a(self, prompt, is_folder, is_todo):
        treenode = self.get_cur_line()
        if treenode is not None and not treenode.is_folder():
            treenode = treenode.parent

        # if treenode is None, then add to root
        default_path = '' if treenode is None else tree.node_path(treenode)
        path = input_path(prompt, default_path)
        if path == '':
            vim.command('echo "Joplin: please enter a new name"')
            return

        items = path.split('/')
        new_name = items[-1]
        folders = items[:-1]
        if not is_folder and len(folders) == 0:
            vim.command('echo "Joplin: a note/todo should add to a notebook"')
            return

        parent = self._find_folder_by_path(folders)
        if parent is None:
            vim.command('echo "Joplin: not such notebook<%s>"' %
                        '/'.join(folders))
            return

        new_node = FolderNode(
            parent_id=parent.node.id,
            title=new_name) if is_folder else NoteNode(
                parent_id=parent.node.id, title=new_name, is_todo=is_todo)
        node = self._joplin.post(new_node)
        if node is not None:
            line = vim.Function('line')('.')
            self._refresh_render(parent)
            vim.Function('cursor')(line, 1)

    def cmd_rn(self, treenode):
        if treenode is None:
            return
        prompt = 'Rename %s to: ' % treenode.node.title
        new_name = vim.Function('input')(prompt, treenode.node.title).decode()
        if new_name == treenode.node.title or new_name == '':
            return
        node = self._joplin.get(FolderNode, treenode.node.id) \
            if treenode.is_folder() \
            else self._joplin.get(NoteNode, treenode.node.id)
        node.title = new_name
        node = self._joplin.put(node)
        treenode.node.title = new_name
        self._render()
        cursor(treenode)

    def cmd_mv(self, treenode):
        if treenode is None:
            return

        origin_parent = treenode.parent
        default_path = '' if treenode.parent is None else tree.node_path(
            treenode.parent)
        prompt = 'Move %s to: ' % treenode.node.title
        path = input_path(prompt, default_path)
        folders = path.split('/')
        parent = self._find_folder_by_path(folders)
        if parent is None or not parent.is_folder():
            vim.command('echo "Joplin: not such notebook<%s>"' % path)
            return

        if parent.node.id == '' and not treenode.is_folder():
            vim.command('echo "Joplin: note/notebook should mv to a notebook"')
            return

        if parent.node.id == treenode.parent.node.id or \
                parent.node.id == treenode.node.id:
            return

        node = self._joplin.get(FolderNode, treenode.node.id) \
            if treenode.is_folder() \
            else self._joplin.get(NoteNode, treenode.node.id)
        node.parent_id = parent.node.id
        node = self._joplin.put(node)
        if node is not None:
            line = vim.Function('line')('.')
            self._refresh(origin_parent)
            self._refresh(parent)
            self._render()
            vim.Function('cursor')(line, 1)

    def cmd_cp(self, treenode):
        if treenode is None:
            return

        if treenode.is_folder():
            vim.command('echo "Joplin: can not copy a notebook"')
            return

        default_path = tree.node_path(treenode.parent)
        prompt = 'Copy %s to: ' % treenode.node.title
        path = input_path(prompt, default_path)
        if path == '':
            vim.command('echo "Joplin: please select a notebook"')
            return

        folders = path.split('/')
        parent = self._find_folder_by_path(folders)
        if parent is None or not parent.is_folder():
            vim.command('echo "Joplin: not such notebook<%s>"' % path)
            return

        if parent.node.id == '':
            vim.command('echo "Joplin: note should copy to a notebook"')
            return

        note = self._joplin.get(NoteNode, treenode.node.id)
        new_note = NoteNode(**note.dict())
        new_note.id = ''
        new_note.created_time = 0
        new_note.updated_time = 0
        new_note.parent_id = parent.node.id
        node = self._joplin.post(new_note)
        if node is not None:
            line = vim.Function('line')('.')
            self._refresh_render(parent)
            vim.Function('cursor')(line, 1)

    def cmd_dd(self, treenode):
        if treenode is None:
            return

        prompt = ''
        if treenode.is_folder():
            prompt = 'Delete notebook <%s>?*All notes and sub-notebooks '\
                'within this notebook will also be deleted* (y/N): ' \
                % treenode.node.title
        else:
            prompt = 'Delete note <%s>? (y/N): ' % treenode.node.title

        cls = FolderNode if treenode.is_folder() else NoteNode
        vim.command('echo "Joplin: %s"' % prompt)
        select = 0
        # 89 == Y, 121 == y, 78 == N, 110 == n, 27 == <esc>, 13 == <cr>
        while True:
            select = vim.Function('getchar')()
            if select in [89, 121]:
                parent = treenode.parent
                self._joplin.delete(cls, treenode.node.id)
                vim.command('redraw!')
                vim.command('echo "Joplin: <%s> deleted"' %
                            treenode.node.title)
                line = vim.Function('line')('.')
                self._refresh_render(parent)

                vim.Function('cursor')(line, 1)
                break
            elif select in [78, 110, 27, 13]:
                vim.command('redraw!')
                vim.command('echo "Joplin: delete aborted"')
                break

    def vmap_cc(self):
        getpos = vim.Function('getpos')
        _, start, _, _ = getpos("'<")
        _, end, _, _ = getpos("'>")
        parents = set()
        for line in range(start, end + 1):
            treenode = self._get_line_node(line)
            if treenode is None or treenode.is_folder():
                continue
            if self._todo_completed_switch(treenode.node.id, True):
                parents.add(treenode.parent)

        if len(parents) > 0:
            for parent in parents:
                self._refresh(parent)

            self._render()
            vim.Function('cursor')(start, 1)

    def vmap_ct(self):
        getpos = vim.Function('getpos')
        _, start, _, _ = getpos("'<")
        _, end, _, _ = getpos("'>")
        parents = set()
        for line in range(start, end + 1):
            treenode = self._get_line_node(line)
            if treenode is None or treenode.is_folder():
                continue
            self._note_type_switch(treenode.node.id)
            parents.add(treenode.parent)

        if len(parents) > 0:
            for parent in parents:
                self._refresh(parent)

            self._render()
            vim.Function('cursor')(start, 1)

    def vmap_dd(self):
        getpos = vim.Function('getpos')
        _, start, _, _ = getpos("'<")
        _, end, _, _ = getpos("'>")
        nodes = list(
            [self._get_line_node(line) for line in range(start, end + 1)])
        nodes = list(filter(lambda node: node is not None, nodes))
        if len(nodes) == 0:
            return

        is_all = False
        prompt = ''
        select = 0
        parents = set()
        for node in nodes:
            if not is_all:
                if node.is_folder():
                    prompt = 'Delete notebook <%s>?*All notes and '\
                        'sub-notebooks within this notebook will also be '\
                        'deleted* (y/N/a): ' % node.node.title
                else:
                    prompt = 'Delete note <%s>? (y/N/a):' % node.node.title

                vim.command('echo "Joplin: %s"' % prompt)

            # 89 == Y, 121 == y, 78 == N, 110 == n, 27 == <esc>, 13 == <cr>
            # 65 == A, 97 == a
            while True:
                if not is_all:
                    select = vim.Function('getchar')()
                if select in [89, 121, 65, 97]:
                    parents.add(node.parent)
                    cls = FolderNode if node.is_folder() else NoteNode
                    self._joplin.delete(cls, node.node.id)
                    is_all = select in [65, 97]
                    break
                elif select in [78, 110, 27, 13]:
                    vim.command('redraw!')
                    vim.command('echo "Joplin: delete aborted"')
                    break

        line = vim.Function('line')('.')
        for parent in parents:
            self._refresh(parent)

        self._render()
        vim.command('redraw!')
        vim.Function('cursor')(line, 1)

    def vmap_mv(self):
        getpos = vim.Function('getpos')
        _, start, _, _ = getpos("'<")
        _, end, _, _ = getpos("'>")
        line = vim.Function('line')('.')
        current_node = self._get_line_node(line)
        origin_parent = current_node.parent
        default_path = '' if origin_parent is None \
            else tree.node_path(origin_parent)
        prompt = 'Move selected to: '
        path = input_path(prompt, default_path)
        folders = path.split('/')
        parent = self._find_folder_by_path(folders)
        if parent is None or not parent.is_folder():
            vim.command('echo "Joplin: not such notebook<%s>"' % path)
            return

        if parent.node.id == '' and not parent.is_folder():
            vim.command('echo "Joplin: note/notebook should mv to a notebook"')
            return

        new_parent = set()
        new_parent.add(parent)
        for line in range(start, end + 1):
            treenode = self._get_line_node(line)
            if treenode is None:
                continue
            if treenode.node.id == parent.node.id or \
                    treenode.parent.node.id == parent.node.id:
                continue
            node = self._joplin.get(FolderNode, treenode.node.id) \
                if treenode.is_folder() \
                else self._joplin.get(NoteNode, treenode.node.id)
            node.parent_id = parent.node.id
            node = self._joplin.put(node)
            new_parent.add(treenode.parent)

        for parent in new_parent:
            self._refresh(parent)

        self._render()
        cursor(origin_parent)

    def search(self, query):
        if query == '':
            return
        nodes = self._joplin.search(query)
        if len(nodes) == 0:
            vim.command('echo "Joplin: search <%s>, not found"' % query)
            return
        items = list([{
            'text': self._joplin.node_path(node) + "| " + node.id,
        } for node in nodes])

        title = 'JoplinSearch "%s"' % query
        result = vim.Function('setqflist')(
            [], 'r', {
                'title': title,
                'items': items,
                'efm': '%%f: %%m',
                'context': 'JoplinSearch',
                'quickfixtextfunc': 'joplin#search#quickfixtext',
            })
        if result == 0:
            size = len(nodes)
            vim.command('copen %d' % (size if size < 10 else 10))
            self._last_query = query
            vim.command('nnoremap <silent><buffer><cr> :python3 '
                        'pyjoplin.win.edit_cur_search("%s")<cr>' % query)

    def edit_cur_search(self, last_query):
        line = vim.Function('line')('.')
        content = vim.Function('getline')(line).decode()
        items = content.split('|')
        if len(items) < 2:
            return
        id = items[-1].strip()
        note = self._joplin.get(NoteNode, id)
        curbufnr = vim.Function('bufnr')('%')
        treebufnr = vim.Function('bufnr')(bufname())
        buflist = vim.Function('tabpagebuflist')()
        buflist = list(
            filter(lambda nr: nr not in [curbufnr, treebufnr], buflist))
        bufnr = buflist[0] if len(buflist) > 0 else treebufnr
        reopen = bufnr == treebufnr
        winnr = vim.Function('bufwinnr')(bufnr)
        vim.command('%dwincmd w' % winnr)
        self._edit_note('edit', reopen, note, 0)
        vim.Function('setqflist')([], 'a', {'idx': line})
        if self._last_query != '':
            vim.command('/%s' % self._last_query)

    # ============================== note cmds
    def cmd_note_info(self):
        note_id = vim.current.buffer.vars.get('joplin_note_id', b'').decode()
        if note_id == '':
            return

        note = self._joplin.get(NoteNode, note_id, ['body'])
        if note is None:
            vim.command('echo "Joplin: not such node <%s>"' % note_id)
            return
        title = ' Information for %s ' % note.title
        path = self._joplin.node_path(note)
        tags = list([tag.title for tag in self._joplin.get_note_tags(note_id)])
        infos = []
        infos.append(NoteInfo('Id', note_id))
        infos.append(NoteInfo('Path', path))
        infos.append(NoteInfo('Markdown link', note.markdown_link()))
        infos.append(NoteInfo('Update time', strftime(note.updated_time)))
        infos.append(NoteInfo('Create time', strftime(note.created_time)))
        infos.append(NoteInfo('Tags', str(tags)))
        max_tag_len = max([len(info.tag) for info in infos])

        props = [{
            'type': 'joplin_popup_info_tag',
            'col': 1,
            'length': max_tag_len,
        }]
        text = list([{
            'text': info.text(max_tag_len),
            'props': props
        } for info in infos])
        text.append({
            'text':
            variable.info_popup_guide,
            'props': [{
                'type': 'joplin_popup_guide',
                'col': 1,
                'length': len(variable.info_popup_guide),
            }]
        })

        vim.Function('popup_dialog')(text, {
            'title': title,
            'filter': 'joplin#popup#info_filter',
            'highlight': 'JoplinInfoWin',
            'mapping': 0,
        })

    def cmd_tag_add(self, title):
        if title == '':
            return

        note_id = vim.current.buffer.vars.get('joplin_note_id', b'').decode()
        if note_id == '':
            return
        # the note has the tag
        had_titles = list(
            [tag.title for tag in self._joplin.get_note_tags(note_id)])
        if title in had_titles:
            return
        tags = self._joplin.get_all(TagNode)
        # tag exists
        tags = list(filter(lambda tag: tag.title == title, tags))
        if len(tags) > 0:
            find = tags[0]
        else:
            find = self._joplin.post(TagNode(title=title))
        if find is not None:
            self._joplin.post_tag_note(find.id, note_id)

    def cmd_tag_del(self, title):
        if title == '':
            return
        note_id = vim.current.buffer.vars.get('joplin_note_id', b'').decode()
        if note_id == '':
            return
        tags = list(
            filter(lambda tag: tag.title == title,
                   self._joplin.get_note_tags(note_id)))
        if len(tags) > 0:
            self._joplin.delete_tag_note(tags[0].id, note_id)

    def cmd_note_type_switch(self):
        note_id = vim.current.buffer.vars.get('joplin_note_id', b'').decode()
        if note_id == '':
            return

        self._note_type_switch(note_id)
        line = vim.current.buffer.vars.get('joplin_treenode_line', -1)
        if line != -1:
            self._refresh_treenode_line(line)

    def cmd_todo_completed_switch(self):
        note_id = vim.current.buffer.vars.get('joplin_note_id', b'').decode()
        if note_id == '':
            return

        if not self._todo_completed_switch(note_id):
            return
        line = vim.current.buffer.vars.get('joplin_treenode_line', -1)
        if line != -1:
            self._refresh_treenode_line(line)

    def cmd_resource_attach(self, filepath):
        title = os.path.basename(filepath)
        resource = ResourceNode(title=title)
        resource = self._joplin.post_resource(filepath, resource)
        if resource is None or resource.id is None:
            vim.command('echo "Joplin: attach resource failed"')
            return
        insert_markdown_link(resource)

    def cmd_link_resource(self, title):
        resources = self._joplin.get_all(ResourceNode)
        matched = list(
            filter(lambda resource: resource.title == title, resources))
        if len(matched) == 0:
            vim.command('echo "Joplin: not such resource <%s>"' % title)
            return
        insert_markdown_link(matched[0])

    def cmd_link_node(self, title):
        path = title.split('/')
        root = self._find_node_by_path(path)
        if root is None:
            vim.command('echo "Joplin: not such note: %s"' % title)
            return
        insert_markdown_link(root.node)

    def _base_line(self):
        return len(variable.window_title) + (len(variable.help_lines)
                                             if self._has_help else 0)

    def get_cur_line(self):
        lineno = int(vim.eval('line(".")'))
        return self._get_line_node(lineno)

    def _get_line_node(self, lineno):
        if lineno <= self._base_line():
            return None
        return find_treenode(self._root, lineno)

    def _refresh_treenode_line(self, line):
        winnr = vim.Function('bufwinnr')(bufname())
        if winnr <= 0:
            return
        winnr_saved = vim.Function('winnr')()
        lazyredraw_saved = vim.options['lazyredraw']
        vim.options['lazyredraw'] = True
        vim.command('%dwincmd w' % winnr)
        treenode = self._get_line_node(line)
        if treenode is not None and not treenode.is_folder():
            treenode = treenode.parent
        self._refresh_render(treenode)
        vim.Function('cursor')(line, 1)
        vim.command('%dwincmd w' % winnr_saved)
        vim.command('redraw!')
        vim.options['lazyredraw'] = lazyredraw_saved

    def _find_node_by_path(self, path):
        path = filter(lambda p: p != '', path)
        root = self._root
        # todo delete root checker
        if root is None:
            return
        for p in path:
            match = list(
                filter(lambda node: node.node.title == p, root.children))
            if len(match) == 0:
                return None
            root = match[0]

        return root if root.node is not None else None

    def _find_folder_by_path(self, path):
        node = self._find_node_by_path(path)
        return node if node is not None and node.is_folder() else None

    def _note_type_switch(self, note_id):
        note = self._joplin.get(NoteNode, note_id)
        note.is_todo ^= 1
        note.todo_completed = 0
        self._joplin.put(note)

    def _todo_completed_switch(self, note_id, silent=False):
        note = self._joplin.get(NoteNode, note_id)
        if not note.is_todo:
            if not silent:
                vim.command('echo "Joplin: not a todo"')

            return False
        note.todo_completed ^= 1
        self._joplin.put(note)
        return True


class NoteInfo(object):
    def __init__(self, tag, data):
        self.tag = tag
        self.data = data

    def text(self, tag_len):
        padding = (tag_len - len(self.tag)) * ' '
        return self.tag + padding + ' : ' + self.data


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
    vim.current.window.options['cursorline'] = True
    vim.current.window.options['number'] = options.number != 0
    vim.current.window.options['relativenumber'] = options.relativenumber != 0


def set_map():
    for lhs in variable.unmap:
        cmd = 'nnoremap <script><silent><buffer>%s <nop>' % lhs
        vim.command(cmd)
    for lhs, rhs in variable.treenode_mapping.items():
        cmd = 'nnoremap <script><silent><buffer>%s <esc>:<c-u>python3 ' \
                'pyjoplin.win.%s(pyjoplin.win.get_cur_line())<cr>' % (lhs, rhs)
        vim.command(cmd)
    for lhs, rhs in variable.win_mapping.items():
        cmd = 'nnoremap <script><silent><buffer>%s <esc>:<c-u>python3 ' \
                'pyjoplin.win.%s()<cr>' % (lhs, rhs)
        vim.command(cmd)

    for lhs, rhs in variable.vmap.items():
        cmd = 'vnoremap <script><silent><buffer>%s :python3 ' \
            'pyjoplin.win.%s()<cr>' % (lhs, rhs)
        vim.command(cmd)


def tree_line(node, indent):
    lines = [node] if node.node.id != '' else []
    node.indent = indent
    if node.is_open() and node.children is not None:
        for node in node.children:
            sub = tree_line(node, indent + 1)
            lines += sub
    return lines


def note_map_command(lhs, command):
    if lhs == '':
        return
    origin = vim.Function('maparg')(lhs, 'n').decode()
    if origin != '':
        return
    vim.command('nnoremap <buffer>%s <esc>:<c-u>%s' % (lhs, command))


def note_local_setting():
    vim.command('autocmd BufWriteCmd <buffer> python3 pyjoplin.win.write()')
    vim.command('autocmd BufWinLeave <buffer> python3 pyjoplin.win.leave()')

    # command for note
    vim.command('command! -buffer -nargs=0 JoplinNoteInfo python3 '
                'pyjoplin.win.cmd_note_info()')
    vim.command('command! -buffer -nargs=0 JoplinNoteTypeSwitch python3 '
                'pyjoplin.win.cmd_note_type_switch()')
    vim.command('command! -buffer -nargs=0 JoplinTodoCompletedSwitch python3 '
                'pyjoplin.win.cmd_todo_completed_switch()')

    # command for tag
    vim.command(
        'command! -buffer -nargs=1 -complete=custom,joplin#complete#tag '
        'JoplinTagAdd python3 '
        'pyjoplin.win.cmd_tag_add(<q-args>)')
    vim.command(
        'command! -buffer -nargs=1 -complete=custom,joplin#complete#note_tag '
        'JoplinTagDel python3 '
        'pyjoplin.win.cmd_tag_del(<q-args>)')

    # command for resource
    vim.command(
        'command! -buffer -nargs=1 -complete=file JoplinResourceAttach python3'
        ' pyjoplin.win.cmd_resource_attach(<q-args>)')

    # command for link
    vim.command('command! -buffer -nargs=1 '
                '-complete=custom,joplin#complete#resource JoplinLinkResource '
                'python3 pyjoplin.win.cmd_link_resource(<q-args>)')
    vim.command('command! -buffer -nargs=1 '
                '-complete=custom,joplin#complete#note JoplinLinkNode '
                'python3 pyjoplin.win.cmd_link_node(<q-args>)')

    note_map_command(options.map_note_info, 'JoplinNoteInfo<cr>')
    note_map_command(options.map_note_type_switch, 'JoplinNoteTypeSwitch<cr>')
    note_map_command(options.map_todo_completed_switch,
                     'JoplinTodoCompletedSwitch<cr>')
    note_map_command(options.map_tag_add, 'JoplinTagAdd ')
    note_map_command(options.map_tag_del, 'JoplinTagDel ')
    note_map_command(options.map_resrouce_attach, 'JoplinResourceAttach ')
    note_map_command(options.map_link_resource, 'JoplinLinkResource ')
    note_map_command(options.map_link_node, 'JoplinLinkNode ')


def insert_markdown_link(node):
    text = node.markdown_link()
    vim.command('normal! a' + text)


def find_treenode(root, lineno):
    nodes = list(filter(lambda node: node.lineno > 0, root.children))
    i = 0
    j = len(nodes) - 1

    if i > j:
        return None
    if nodes[j].lineno < lineno:
        return find_treenode(nodes[j], lineno) if \
            nodes[j].is_folder() else \
            None
    while i <= j:
        mid = int((i + j) / 2)
        if nodes[mid].lineno == lineno:
            return nodes[mid]
        elif nodes[mid].lineno < lineno:
            i = mid + 1
        elif nodes[mid].lineno > lineno:
            j = mid - 1

    mid = i if nodes[i].lineno < lineno else i - 1
    return find_treenode(nodes[mid], lineno) if \
        nodes[mid].is_folder() else \
        None


def cursor(treenode):
    if treenode.lineno > 0:
        vim.Function('cursor')(treenode.lineno, 1)


def go_to_previous_win():
    saved_prev_winnr = vim.current.buffer.vars.get('saved_prev_winnr', -1)
    if saved_prev_winnr > 0:
        vim.command('%dwincmd w' % saved_prev_winnr)
    else:
        vim.command('wincmd w')


def strftime(timestamp):
    return datetime.fromtimestamp(timestamp /
                                  1000.0).strftime('%Y-%m-%d %H:%M:%S')


def input_path(prompt, default_path):
    cmdheight_saved = vim.options['cmdheight']
    if cmdheight_saved < 2:
        vim.options['cmdheight'] = 2
    vim.command('redraw!')
    vim.command('echo " "')
    path = vim.Function('input')(prompt, default_path,
                                 'custom,joplin#complete#folder').decode()
    path = path.strip()
    vim.command('redraw!')
    vim.options['cmdheight'] = cmdheight_saved
    return path


def del_child(root, id):
    if root is None or id == '':
        return
    root.children = list(filter(lambda node: node.node.id != id,
                                root.children))


win = Win()
