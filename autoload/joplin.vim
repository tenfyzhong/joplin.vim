let s:pwd = expand('<sfile>:p:h')
pythonx <<EOF
pwd = vim.eval('s:pwd')
if pwd not in sys.path:
  sys.path.append(pwd)

import jplvim
vim.command('let s:joplin_window_name = "%s"' % jplvim.bufname())
EOF

function! joplin#open()
  if !exists('g:joplin_token')
    echohl WarningMsg | echom "joplin.vim: Please set g:joplin_token first." | echohl None
    return
  endif
  pythonx jplvim.open_window()
endfunction

function! joplin#close()
  pythonx jplvim.close_window()
endfunction

function! joplin#toggle()
  if bufwinnr(s:joplin_window_name) > 0
    call joplin#close()
  else
    call joplin#open()
  endif
endfunction
