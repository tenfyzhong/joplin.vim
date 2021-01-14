#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from datetime import datetime

import vim

from . import options, tree, variable
from .node import FolderNode, NoteNode, ResourceNode, TagNode
from .variable import bufname, get_joplin

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
    'joplin_popup_indicator': 'MenuItemIndicator',
}

for name, highlight in props.items():
    vim.Function('prop_type_add')(name, {'highlight': highlight})


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
                'pyjoplin.treenode_cmd("%s")<cr>' % (lhs, rhs)
        vim.command(cmd)
    for lhs, rhs in variable.win_mapping.items():
        cmd = 'nnoremap <script><silent><buffer>%s <esc>:<c-u>python3 ' \
                'pyjoplin.run("%s")<cr>' % (lhs, rhs)
        vim.command(cmd)


def open_window():
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
    render()
    last_line = vim.current.buffer.vars.get('saved_last_line',
                                            len(variable.window_title) + 1)
    vim.Function('cursor')(last_line, 1)


def close_window():
    bufname_ = bufname()
    winnr = vim.Function('bufwinnr')(bufname_)
    if winnr > 0:
        vim.command('%dclose' % winnr)


def toggle_window():
    if vim.Function('bufwinnr')(bufname()) > 0:
        close_window()
    else:
        open_window()


def write(note_id, **kwargs):
    note = get_joplin().get(NoteNode, note_id)
    if note is None:
        return

    note.body = '\n'.join(vim.current.buffer[:])
    get_joplin().put(note)


def saveas(**kwargs):
    if 'path' not in kwargs:
        vim.command('echo "Joplin: please enter a name"')
        return
    path = kwargs['path']
    if path == '':
        vim.command('echo "Joplin: please enter a new name"')
        return

    folders = path.split('/')
    parent = find_folder_by_path(folders)
    if parent.node.id == '':
        vim.command('echo "Joplin: not such notebook<%s>"' % path)
        return

    if parent.node.id == '':
        vim.command('echo "Joplin: note should copy to a notebook"')
        return

    is_todo = kwargs.get('is_todo', 0)
    new_title = vim.Function('expand')('%:p:t').decode()
    note = NoteNode()
    body = '\n'.join(vim.current.buffer[:])
    note.parent_id = parent.node.id
    note.title = new_title
    note.body = body
    note.is_todo = is_todo
    note = get_joplin().post(note)
    if note is None:
        vim.command('echo "Joplin: New note failed"')
        return
    refresh_render(parent)
    note_local_setting()
    vim.current.buffer.vars['joplin_note_id'] = note.id
    vim.command('noautocmd w')


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


def render_help(nr):
    lines = variable.help_lines if has_help() else []
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


def render_title(nr):
    for text in variable.window_title:
        vim.current.buffer.append(text, nr)
        prop_add(nr + 1, 'joplin_window_title')
        nr += 1
    return nr


def tree_line(node, indent):
    lines = [node] if node.node.id != '' else []
    node.indent = indent
    if node.is_open():
        for node in node.children:
            sub = tree_line(node, indent + 1)
            lines += sub
    return lines


def render_nodes(nr):
    root = variable.get_root()
    if root is None:
        return nr

    lines = tree_line(root, -1)
    for line in lines:
        vim.current.buffer.append(
            line.text(options.icon_open, options.icon_close, options.icon_note,
                      options.icon_todo, options.icon_completed), nr)
        line.lineno = nr + 1
        prop_type = line.prop_type()
        prop_add(nr + 1, prop_type)
        nr += 1

    return nr


def render():
    winnr_saved = vim.Function('winnr')()
    winnr = vim.Function('bufwinnr')(bufname())
    if winnr < 0:
        return
    vim.command('%dwincmd w' % winnr)
    vim.current.buffer.options['modifiable'] = True
    del vim.current.buffer[:]
    nr = 0
    nr = render_help(nr)
    nr = render_title(nr)
    nr = render_nodes(nr)
    # delete empty line
    del vim.current.buffer[nr]
    vim.current.buffer.options['modifiable'] = False
    if winnr_saved != winnr:
        vim.command('%dwincmd w' % winnr_saved)


def edit_note(command, reopen_tree, note, joplin_treenode_line):
    lazyredraw_saved = vim.options['lazyredraw']
    winview_saved = vim.Function('winsaveview')()
    undolevel_saved = vim.options['undolevels']
    vim.options['undolevels'] = -1
    dirname = vim.eval('tempname()')
    os.mkdir(dirname)
    filename = dirname + '/' + note.title + '.md'
    vim.command('silent %s %s' % (command, filename))
    vim.current.buffer.vars['joplin_note_id'] = note.id
    vim.current.buffer.vars['joplin_path'] = get_joplin().node_path(note)
    vim.current.buffer.options['filetype'] = 'joplin.markdown'
    if joplin_treenode_line > 0:
        vim.current.buffer.vars['joplin_treenode_line'] = joplin_treenode_line

    vim.options['lazyredraw'] = True
    vim.current.buffer[:] = note.body.split('\n')
    vim.command('silent noautocmd w')
    if reopen_tree:
        # check joplin window
        # reopen if not exist
        winnr = vim.Function('bufwinnr')(bufname())
        if winnr < 0:
            note_bufname = vim.Function('bufname')()
            open_window()
            vim.Function('winrestview')(winview_saved)
            winnr = vim.Function('bufwinnr')(note_bufname)
            vim.command('%dwincmd w' % winnr)

    vim.command('redraw!')
    vim.command('silent call joplin#statusline#refresh()')

    vim.options['lazyredraw'] = lazyredraw_saved
    vim.options['undolevels'] = undolevel_saved
    vim.Function('cursor')(1, 1)
    note_local_setting()


def edit(command, treenode):
    treenode.fetch_note(get_joplin())
    edit_note(command, True, treenode.node, treenode.lineno)


def note_map_command(lhs, command):
    if lhs == '':
        return
    vim.command('nnoremap <buffer>%s <esc>:<c-u>%s' % (lhs, command))


def note_local_setting():
    vim.command(
        'autocmd BufWritePost <buffer> python3 pyjoplin.note_cmd("write")')

    # command for note
    vim.command('command! -buffer -nargs=0 JoplinNoteInfo python3 '
                'pyjoplin.note_cmd("cmd_note_info")')
    vim.command('command! -buffer -nargs=0 JoplinNoteTypeConvert python3 '
                'pyjoplin.note_cmd("cmd_note_type_convert")')
    vim.command('command! -buffer -nargs=0 JoplinNoteCompleteConvert python3 '
                'pyjoplin.note_cmd("cmd_note_complete_convert")')

    # command for tag
    vim.command(
        'command! -buffer -nargs=1 -complete=custom,joplin#complete#tag '
        'JoplinTagAdd python3 '
        'pyjoplin.note_cmd("cmd_tag_add", title=<q-args>)')
    vim.command(
        'command! -buffer -nargs=1 -complete=custom,joplin#complete#note_tag '
        'JoplinTagDel python3 '
        'pyjoplin.note_cmd("cmd_tag_del", title=<q-args>)')

    # command for resource
    vim.command(
        'command! -buffer -nargs=1 -complete=file JoplinResourceAttach python3'
        ' pyjoplin.note_cmd("cmd_resource_attach", file=<q-args>)')

    # command for link
    vim.command(
        'command! -buffer -nargs=1 '
        '-complete=custom,joplin#complete#resource JoplinLinkResource '
        'python3 pyjoplin.note_cmd("cmd_link_resource", title=<q-args>)')
    vim.command('command! -buffer -nargs=1 '
                '-complete=custom,joplin#complete#note JoplinLinkNote '
                'python3 pyjoplin.note_cmd("cmd_link_note", title=<q-args>)')

    note_map_command(options.map_note_info, 'JoplinNoteInfo<cr>')
    note_map_command(options.map_note_type_convert,
                     'JoplinNoteTypeConvert<cr>')
    note_map_command(options.map_note_complete_convert,
                     'JoplinNoteCompleteConvert<cr>')
    note_map_command(options.map_tag_add, 'JoplinTagAdd ')
    note_map_command(options.map_tag_del, 'JoplinTagDel ')
    note_map_command(options.map_resrouce_attach, 'JoplinResourceAttach ')
    note_map_command(options.map_link_resource, 'JoplinLinkResource ')
    note_map_command(options.map_link_note, 'JoplinLinkNote ')


def refresh_render(treenode):
    refresh(treenode)
    render()


def refresh(treenode):
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
    treenode.fetch_folder(get_joplin(), options.pin_todo,
                          options.hide_completed, options.folder_order_by,
                          options.folder_order_desc, options.note_order_by,
                          options.note_order_desc)
    for child in treenode.children:
        refresh(child)


# ============================== run functions
def run(funcname, **kwargs):
    return eval('%s(**kwargs)' % funcname)


def treenode_cmd(funcname, **kwargs):
    treenode = get_cur_line()
    if treenode is None:
        return
    return eval("%s(treenode, **kwargs)" % funcname)


def note_cmd(funcname, **kwargs):
    note_id = vim.current.buffer.vars.get('joplin_note_id', b'').decode()
    if note_id == '':
        return
    return eval("%s(note_id, **kwargs)" % funcname)


# ============================== complete
def complete_note_tag():
    note_id = vim.current.buffer.vars.get('joplin_note_id', b'').decode()
    if note_id == '':
        return ''
    tags = list([tag.title for tag in get_joplin().get_note_tags(note_id)])
    tags = sorted(tags)
    return '\n'.join(tags)


def complete_resource():
    resources = get_joplin().get_all(ResourceNode)
    titles = list([resource.title for resource in resources])
    titles = sorted(list(set(titles)))
    return '\n'.join(titles)


def complete_tag():
    tags = get_joplin().get_all(TagNode)
    titles = list([tag.title for tag in tags])
    titles = sorted(list(set(titles)))
    return '\n'.join(titles)


def complete_note(arg_lead):
    path = arg_lead.split(r'/')
    path = path[:-1]
    root = find_folder_by_path(path)
    if root is None:
        return ''
    root.fetch_folder(get_joplin(), options.pin_todo, options.hide_completed,
                      options.folder_order_by, options.folder_order_desc,
                      options.note_order_by, options.note_order_desc)
    dirname = tree.node_path(root)
    lines = list([dirname + '/' + node.node.title for node in root.children])
    lines = list(
        map(lambda line: line[1:] if line.startswith('/') else line, lines))
    return '\n'.join(lines)


def complete_folder(arg_lead):
    path = arg_lead.split(r'/')
    path = path[:-1]
    root = find_folder_by_path(path)
    if root is None:
        return ''
    dirname = tree.node_path(root)
    lines = list([
        dirname + '/' + node.node.title for node in root.children
        if node.is_folder()
    ])
    lines = list(
        map(lambda line: line[1:] if line.startswith('/') else line, lines))
    text = '\n'.join(lines)
    return text


def words2bvar(**kwargs):
    if 'var' not in kwargs or 'wordsfunc' not in kwargs:
        return
    wordsfunc = kwargs['wordsfunc']
    titles = eval(wordsfunc + '()')
    return titles


# ============================== treenode cmd
def cmd_o(treenode):
    if treenode.is_folder():
        if treenode.is_open():
            treenode.close()
        else:
            treenode.open(get_joplin(), options.pin_todo,
                          options.hide_completed, options.folder_order_by,
                          options.folder_order_desc, options.note_order_by,
                          options.note_order_desc)
        saved_pos = vim.eval('getcurpos()')
        render()
        vim.Function('setpos')('.', saved_pos)
    else:
        go_to_previous_win()
        edit('edit', treenode)


def cmd_t(treenode):
    if not treenode.is_folder():
        edit('tabnew', treenode)


def cmd_i(treenode):
    if not treenode.is_folder():
        go_to_previous_win()
        edit('split', treenode)


def cmd_s(treenode):
    if not treenode.is_folder():
        go_to_previous_win()
        edit('vsplit', treenode)


def open_recusively(treenode):
    if treenode.is_folder() and not treenode.is_open():
        treenode.open(get_joplin(), options.pin_todo, options.hide_completed,
                      options.folder_order_by, options.folder_order_desc,
                      options.note_order_by, options.note_order_desc)

    for child in treenode.children:
        open_recusively(child)


def cmd_O(treenode):
    if not treenode.is_folder():
        return
    if treenode.is_open():
        close_recurisive(treenode)
    else:
        open_recusively(treenode)

    render()
    cursor(treenode)


def cmd_x(treenode):
    parent = treenode.parent
    if parent is None or parent.node.id == '' or not parent.is_open():
        return

    parent.close()
    render()
    cursor(parent)


def close_recurisive(node):
    if not node.is_folder() or not node.is_open():
        return

    node.close()
    for child in node.children:
        close_recurisive(child)


def cmd_X(treenode):
    if not treenode.is_folder():
        return
    close_recurisive(treenode)
    render()
    cursor(treenode)


def cmd_r(treenode):
    lastnode = treenode
    if not treenode.is_folder():
        treenode = treenode.parent
    refresh_render(treenode)
    cursor(lastnode)
    vim.command('echo "Joplin: Refreshed!"')


def cmd_R(treenode):
    lastnode = treenode
    while treenode.parent is not None:
        treenode = treenode.parent
    refresh_render(treenode)
    cursor(lastnode)
    vim.command('echo "Joplin: Refreshed!"')


def cmd_P(treenode):
    while treenode.parent is not None:
        treenode = treenode.parent
    cursor(treenode)


def cmd_p(treenode):
    treenode = treenode.parent if treenode.parent is not None else treenode
    cursor(treenode)


def cmd_K(treenode):
    if len(treenode.parent.children) > 0:
        cursor(treenode.parent.children[0])


def cmd_J(treenode):
    if len(treenode.parent.children) > 0:
        cursor(treenode.parent.children[-1])


def cmd_ctrl_j(treenode):
    nodes = treenode.parent.children
    i = treenode.child_index_of_parent + 1
    if i < len(nodes):
        cursor(nodes[i])


def cmd_ctrl_k(treenode):
    nodes = treenode.parent.children
    i = treenode.child_index_of_parent - 1
    if i >= 0:
        cursor(nodes[i])


def cmd_q():
    close_window()


def cmd_question_mark():
    joplin_help = has_help()
    vim.current.buffer.vars['joplin_help'] = not joplin_help
    render()
    vim.Function('cursor')(1, 1)


def cmd_ab(**kwargs):
    cmd_a('Add notebook to path: ', True, 0)


def cmd_at(treenode, **kwargs):
    cmd_a('Add todo to path: ', False, 1)


def cmd_an(treenode, **kwargs):
    cmd_a('Add note to path: ', False, 0)


def cmd_a(prompt, is_folder, is_todo):
    treenode = get_cur_line()
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
        vim.command('echo "Joplin: a note should add to a notebook"')
        return

    parent = find_folder_by_path(folders)
    if parent.node.id == '':
        vim.command('echo "Joplin: not such notebook<%s>"' % '/'.join(folders))
        return

    new_node = FolderNode(
        parent_id=parent.node.id, title=new_name) if is_folder else NoteNode(
            parent_id=parent.node.id, title=new_name, is_todo=is_todo)
    node = get_joplin().post(new_node)
    if node is not None:
        line = vim.Function('line')('.')
        refresh_render(parent)
        vim.Function('cursor')(line, 1)


def cmd_mv(treenode):
    default_path = '' if treenode.parent is None else tree.node_path(
        treenode.parent)
    prompt = 'Move %s to: ' % treenode.node.title
    path = input_path(prompt, default_path)
    folders = path.split('/')
    parent = find_folder_by_path(folders)
    if parent is None or not parent.is_folder():
        vim.command('echo "Joplin: not such notebook<%s>"' % path)
        return

    if parent.node.id == '':
        vim.command('echo "Joplin: note should mv to a notebook"')
        return

    if parent.node.id == treenode.parent.node.id:
        return

    node = get_joplin().get(FolderNode, treenode.node.id) \
        if treenode.is_folder() \
        else get_joplin().get(NoteNode, treenode.node.id)
    node.parent_id = parent.node.id
    node = get_joplin().put(node)
    if node is not None:
        line = vim.Function('line')('.')
        refresh(parent)
        refresh(treenode.parent)
        render()
        vim.Function('cursor')(line, 1)


def cmd_cp(treenode):
    if treenode.is_folder():
        vim.command('echo "Joplin: can not copy a notebook"')
        return

    default_path = tree.node_path(treenode.parent)
    prompt = 'Copy %s to: ' % treenode.node.title
    path = input_path(prompt, default_path)
    if path == '':
        vim.command('echo "Joplin: please enter a new name"')
        return

    folders = path.split('/')
    parent = find_folder_by_path(folders)
    if parent is None or not parent.is_folder():
        vim.command('echo "Joplin: not such notebook<%s>"' % path)
        return

    if parent.node.id == '':
        vim.command('echo "Joplin: note should copy to a notebook"')
        return

    note = get_joplin().get(NoteNode, treenode.node.id)
    new_note = NoteNode(**note.dict())
    new_note.id = ''
    new_note.created_time = 0
    new_note.updated_time = 0
    new_note.parent_id = parent.node.id
    node = get_joplin().post(new_note)
    if node is not None:
        line = vim.Function('line')('.')
        refresh_render(parent)
        vim.Function('cursor')(line, 1)


def cmd_dd(treenode):
    prompt = ''
    if treenode.is_folder():
        prompt = 'Delete notebook <%s>?*All notes and sub-notebooks within ' \
            'this notebook will also be deleted* (y/N): ' % treenode.node.title
    else:
        prompt = 'Delete note <%s>? (y/N)' % treenode.node.title

    cls = FolderNode if treenode.is_folder() else NoteNode
    # select = vim.Function('input')(prompt)
    vim.command('echo "Joplin: %s"' % prompt)
    select = 0
    # 89 == Y, 121 == y, 78 == N, 110 == n, 27 == <esc>, 13 == <cr>
    while True:
        select = vim.Function('getchar')()
        if select in [89, 121]:
            get_joplin().delete(cls, treenode.node.id)
            vim.command('redraw!')
            vim.command('echo "Joplin: <%s> deleted"' % treenode.node.title)
            line = vim.Function('line')('.')
            # if treenode.parent is None:
            #     variable.del_rootnode(treenode.node.id)
            #     render()
            # else:
            treenode.parent.children = variable.delete_node_in_list(
                treenode.parent.children, treenode.node.id)
            render()

            vim.Function('cursor')(line, 1)
            break
        elif select in [78, 110, 27, 13]:
            vim.command('redraw!')
            vim.command('echo "Joplin: delete aborted"')
            break


_last_query = ''


def search(**kwargs):
    global _last_query
    if 'query' not in kwargs:
        return
    query = kwargs['query']
    if query == '':
        return
    joplin = get_joplin()
    if joplin is None:
        return
    nodes = joplin.search(query)
    if len(nodes) == 0:
        vim.command('echo "Joplin: search <%s>, not found"' % query)
        return
    items = list([{
        'text': joplin.node_path(node) + "| " + node.id,
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
        _last_query = query
        vim.command('nnoremap <silent><buffer><cr> :python3 '
                    'pyjoplin.run("edit_cur_search")<cr>')


def edit_cur_search():
    line = vim.Function('line')('.')
    content = vim.Function('getline')(line).decode()
    items = content.split('|')
    if len(items) < 2:
        return
    id = items[-1].strip()
    joplin = get_joplin()
    if joplin is None:
        return
    note = joplin.get(NoteNode, id)
    curbufnr = vim.Function('bufnr')('%')
    treebufnr = vim.Function('bufnr')(bufname())
    buflist = vim.Function('tabpagebuflist')()
    buflist = list(filter(lambda nr: nr not in [curbufnr, treebufnr], buflist))
    bufnr = buflist[0] if len(buflist) > 0 else treebufnr
    reopen = bufnr == treebufnr
    winnr = vim.Function('bufwinnr')(bufnr)
    vim.command('%dwincmd w' % winnr)
    edit_note('edit', reopen, note, 0)
    vim.Function('setqflist')([], 'a', {'idx': line})
    if _last_query != '':
        vim.command('/%s' % _last_query)


# ============================== note cmds
class NoteInfo(object):
    def __init__(self, tag, data):
        self.tag = tag
        self.data = data

    def text(self, tag_len):
        padding = (tag_len - len(self.tag)) * ' '
        return self.tag + padding + ' : ' + self.data


def cmd_note_info(note_id, **kwargs):
    note = get_joplin().get(NoteNode, note_id, ['body'])
    if note is None:
        vim.command('echo "Joplin: not such node <%s>"' % note_id)
        return
    title = ' Information for %s ' % note.title
    path = get_joplin().node_path(note)
    tags = list([tag.title for tag in get_joplin().get_note_tags(note_id)])
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
        'highlight': 'InfoMenu',
        'mapping': 0,
    })


def cmd_tag_add(note_id, **kwargs):
    if 'title' not in kwargs:
        return
    title = kwargs['title']
    # the note has the tag
    had_titles = list(
        [tag.title for tag in get_joplin().get_note_tags(note_id)])
    if title in had_titles:
        return
    tags = get_joplin().get_all(TagNode)
    # tag exists
    tags = list(filter(lambda tag: tag.title == title, tags))
    if len(tags) > 0:
        find = tags[0]
    else:
        find = get_joplin().post(TagNode(title=title))
    if find is not None:
        get_joplin().post_tag_note(find.id, note_id)


def cmd_tag_del(note_id, **kwargs):
    if 'title' not in kwargs:
        return
    title = kwargs['title']
    tags = list(
        filter(lambda tag: tag.title == title,
               get_joplin().get_note_tags(note_id)))
    if len(tags) > 0:
        get_joplin().delete_tag_note(tags[0].id, note_id)


def cmd_note_type_convert(note_id, **kwargs):
    note = get_joplin().get(NoteNode, note_id)
    note.is_todo ^= 1
    note.todo_completed = 0
    get_joplin().put(note)
    line = vim.current.buffer.vars.get('joplin_treenode_line', -1)
    if line != -1:
        refresh_treenode_line(line)


def cmd_note_complete_convert(note_id, **kwargs):
    note = get_joplin().get(NoteNode, note_id)
    if not note.is_todo:
        vim.command('echo "Joplin: not a todo"')
        return
    note.todo_completed ^= 1
    get_joplin().put(note)
    line = vim.current.buffer.vars.get('joplin_treenode_line', -1)
    if line != -1:
        refresh_treenode_line(line)


def cmd_resource_attach(note_id, **kwargs):
    if 'file' not in kwargs:
        return
    filepath = kwargs['file']
    title = os.path.basename(filepath)
    resource = ResourceNode(title=title)
    resource = get_joplin().post_resource(filepath, resource)
    if resource.id == '':
        vim.command('echo "Joplin: attach resource failed"')
        return
    insert_resource(resource)


def cmd_link_resource(note_id, **kwargs):
    if 'title' not in kwargs:
        vim.command('echo "Joplin: please select a resource"')
        return
    title = kwargs['title']
    resources = get_joplin().get_all(ResourceNode)
    matched = list(filter(lambda resource: resource.title == title, resources))
    if len(matched) == 0:
        vim.command('echo "Joplin: not such resource <%s>"' % title)
        return
    insert_resource(matched[0])


def cmd_link_note(note_id, **kwargs):
    if 'title' not in kwargs:
        vim.command('echo "Joplin: please select a note"')
        return
    title = kwargs['title']
    path = title.split('/')
    root = find_node_by_path(path)
    if root is None:
        vim.command('echo "Joplin: not such note: %s"' % title)
        return
    vim.command('normal! a' + root.node.markdown_link())


# ============================== util for cmd function
def insert_resource(resource):
    text = resource.markdown_link()
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


def base_line():
    return len(variable.window_title) + (len(variable.help_lines)
                                         if has_help() else 0)


def get_cur_line():
    lineno = int(vim.eval('line(".")'))
    if lineno <= base_line():
        return None
    return find_treenode(variable.get_root(), lineno)


def cursor(treenode):
    if treenode.lineno > 0:
        vim.Function('cursor')(treenode.lineno, 1)


def refresh_treenode_line(line):
    winnr = vim.Function('bufwinnr')(bufname())
    if winnr <= 0:
        return
    winnr_saved = vim.Function('winnr')()
    lazyredraw_saved = vim.options['lazyredraw']
    vim.options['lazyredraw'] = True
    vim.command('%dwincmd w' % winnr)
    treenode = find_treenode(variable.get_root(), line)
    if treenode is not None and not treenode.is_folder():
        treenode = treenode.parent
    refresh_render(treenode)
    vim.command('%dwincmd w' % winnr_saved)
    vim.command('redraw!')
    vim.options['lazyredraw'] = lazyredraw_saved


def go_to_previous_win():
    saved_prev_winnr = vim.current.buffer.vars.get('saved_prev_winnr', -1)
    if saved_prev_winnr > 0:
        vim.command('%dwincmd w' % saved_prev_winnr)
    else:
        vim.command('wincmd w')


def has_help():
    return vim.current.buffer.vars.get('joplin_help', False)


def strftime(timestamp):
    return datetime.fromtimestamp(timestamp /
                                  1000.0).strftime('%Y-%m-%d %H:%M:%S')


def find_node_by_path(path):
    path = filter(lambda p: p != '', path)
    root = variable.get_root()
    if root is None:
        return
    for p in path:
        match = list(filter(lambda node: node.node.title == p, root.children))
        if len(match) == 0:
            return None
        root = match[0]

    return root if root.node is not None else None


def find_folder_by_path(path):
    node = find_node_by_path(path)
    return node if node is not None and node.is_folder() else None


def input_path(prompt, default_path):
    cmdheight_saved = vim.options['cmdheight']
    if cmdheight_saved < 2:
        vim.options['cmdheight'] = 2
    vim.command('redraw!')
    # vim.command('echo "%s"' % prompt1)
    vim.command('echo " "')
    path = vim.Function('input')(prompt, default_path,
                                 'custom,joplin#complete#folder').decode()
    path = path.strip()
    vim.command('redraw!')
    vim.options['cmdheight'] = cmdheight_saved
    return path
