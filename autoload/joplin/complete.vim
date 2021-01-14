python3 << EOF
import vim
import pyjoplin
pyjoplin.win.init()
health = pyjoplin.win.health()
if not health:
    vim.command('echo "Joplin: please run joplin.app first"')
    vim.command('finish')
EOF

function! joplin#complete#tag(A, L, P)
  python3 vim.command('let text = "%s"' % pyjoplin.win.complete_tag())
  return text
endfunction

function! joplin#complete#note_tag(A, L, P)
  python3 vim.command('let text = "%s"' % pyjoplin.win.complete_note_tag())
  return text
endfunction

function! joplin#complete#resource(A, L, P)
  python3 vim.command('let text = "%s"' % pyjoplin.win.complete_resource())
  return text
endfunction

function! joplin#complete#note(A, L, P)
  python3 vim.command('let text = "%s"' % pyjoplin.win.complete_note(vim.eval('a:A')))
  return text
endfunction

function! joplin#complete#folder(A, L, P)
  python3 vim.command('let text = "%s"' % pyjoplin.win.complete_folder(vim.eval('a:A')))
  return text
endfunction
