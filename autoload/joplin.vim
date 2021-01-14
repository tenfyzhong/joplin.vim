let s:pwd = expand('<sfile>:p:h')

python3 import vim
python3 import pyjoplin

function! joplin#open() abort
  python3 pyjoplin.run('open_window')
endfunction

function! joplin#close() abort
  python3 pyjoplin.run('close_window')
endfunction

function! joplin#toggle() abort
  python3 pyjoplin.run('toggle_window')
endfunction

function! joplin#saveas(is_todo, folder) abort
  python3 pyjoplin.run('saveas', is_todo=vim.eval('a:is_todo'), path=vim.eval('a:folder'))
endfunction

function! joplin#search(query) abort
  python3 pyjoplin.run('search', query=vim.eval('a:query'))
endfunction

