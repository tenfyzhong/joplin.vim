let s:pwd = expand('<sfile>:p:h')


python3 <<EOF
pwd = vim.eval('s:pwd')
if pwd not in sys.path:
  sys.path.append(pwd)

import pyjoplin
EOF

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
  exec printf("python3 pyjoplin.run('saveas', is_todo=%d, path='%s')", a:is_todo, a:folder)
endfunction

function! joplin#search(query) abort
  exec printf("python3 pyjoplin.run('search', query='%s')", a:query)
endfunction

function! joplin#joplin_folder_complete(A, L, P) abort
  let var = 'folder_complete_word'
  exec printf("python3 pyjoplin.run('folder_match_text', arg_lead='%s', var='%s')", a:A, var)
  let text = get(b:, var, '')
  return text
endfunction

