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