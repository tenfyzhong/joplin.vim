let s:pwd = expand('<sfile>:p:h')


python3 <<EOF
pwd = vim.eval('s:pwd')
if pwd not in sys.path:
  sys.path.append(pwd)

import pyjoplin
EOF

function! joplin#open()
  python3 pyjoplin.open_window()
endfunction

function! joplin#close()
  python3 pyjoplin.close_window()
endfunction

function! joplin#toggle()
  python3 pyjoplin.toggle_window()
endfunction

