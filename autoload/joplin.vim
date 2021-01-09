let s:pwd = expand('<sfile>:p:h')


python3 <<EOF
pwd = vim.eval('s:pwd')
if pwd not in sys.path:
  sys.path.append(pwd)

import pyjoplin
EOF

function! joplin#open()
  python3 pyjoplin.run('open_window')
endfunction

function! joplin#close()
  python3 pyjoplin.run('close_window')
endfunction

function! joplin#toggle()
  python3 pyjoplin.run('toggle_window')
endfunction

function! joplin#save_as(folder) abort
  exec printf("python3 pyjoplin.run('saveas', folder='%s')", a:folder)
endfunction

function! joplin#joplin_folder_complete(A, L, P) abort
  let var = 'folder_complete_word'
  exec printf("python3 pyjoplin.run('folder_match_text', arg_lead='%s', var='%s')", a:A, var)
  let text = get(b:, var, '')
  return text
endfunction

