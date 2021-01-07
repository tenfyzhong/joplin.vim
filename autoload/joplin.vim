let s:pwd = expand('<sfile>:p:h')
pythonx <<EOF
pwd = vim.eval('s:pwd')
if pwd not in sys.path:
  sys.path.append(pwd)

import jplvim
EOF

function! joplin#open()
  pythonx jplvim.open_window()
endfunction

function! joplin#close()
  pythonx jplvim.close_window()
endfunction

function! joplin#toggle()
  pythonx jplvim.toggle_window()
endfunction
