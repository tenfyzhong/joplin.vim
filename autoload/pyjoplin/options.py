#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim

token = vim.vars.get('joplin_token', b'').decode()
host = vim.vars.get('joplin_host', b'127.0.0.1').decode()
port = vim.vars.get('joplin_port', 41184)
window_width = vim.vars.get('joplin_window_width', 30)
icon_open = vim.vars.get('joplin_icon_open', b'-').decode()
icon_close = vim.vars.get('joplin_icon_close', b'+').decode()
icon_todo = vim.vars.get('joplin_icon_todo', b'[ ]').decode()
icon_completed = vim.vars.get('joplin_icon_completed', b'[x]').decode()
icon_note = vim.vars.get('joplin_icon_note', b'').decode()
pin_todo = vim.vars.get('joplin_pin_todo', 1)
hide_completed = vim.vars.get('joplin_hide_completed', 0)
folder_order_by = vim.vars.get('joplin_notebook_order_by', b'title').decode()
folder_order_desc = vim.vars.get('joplin_notebook_order_desc', 0)
note_order_by = vim.vars.get('joplin_note_order_by', b'updated_time').decode()
note_order_desc = vim.vars.get('joplin_note_order_desc', 0)
number = vim.vars.get('joplin_number', 0)
relativenumber = vim.vars.get('joplin_relativenumber', 0)
map_note_info = vim.vars.get('joplin_map_note_info', '').decode()
map_note_type_convert = vim.vars.get('joplin_map_note_type_convert',
                                     '').decode()
map_note_complete_convert = vim.vars.get('joplin_map_note_complete_convert',
                                         '').decode()
map_tag_add = vim.vars.get('joplin_map_tag_add', '').decode()
map_tag_del = vim.vars.get('joplin_map_tag_del', '').decode()
map_resrouce_attach = vim.vars.get('joplin_map_resource_attach', '').decode()
map_link_resource = vim.vars.get('joplin_map_link_resource', '').decode()
map_link_note = vim.vars.get('joplin_map_link_note', '').decode()
