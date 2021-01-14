let s:pwd = expand('<sfile>:p:h')

python3 << EOF
import vim
import pyjoplin
pyjoplin.win.init()
health = pyjoplin.win.health()
if not health:
    vim.command('echo "Joplin: please run joplin.app first"')
    vim.command('finish')
EOF

function! joplin#open() abort
  python3 pyjoplin.win.open()
endfunction

function! joplin#close() abort
  python3 pyjoplin.win.close()
endfunction

function! joplin#toggle() abort
  python3 pyjoplin.win.toggle()
endfunction

function! joplin#saveas(is_todo, folder) abort
  python3 pyjoplin.win.saveas(vim.eval('a:is_todo'), vim.eval('a:folder'))
endfunction

function! joplin#search(query) abort
  python3 pyjoplin.win.search(vim.eval('a:query'))
endfunction

