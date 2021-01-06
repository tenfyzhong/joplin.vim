let s:pwd = expand('<sfile>:p:h')
pythonx <<EOF
pwd = vim.eval('s:pwd')
if pwd not in sys.path:
  sys.path.append(pwd)

import jplvim
EOF

function! joplin#open_window()
  pythonx jplvim.open_window()
endfunction

function! joplin#open()
  pythonx jplvim.open()
endfunction
