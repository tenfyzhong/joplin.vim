python3 import vim
python3 import pyjoplin

function! joplin#complete#tag(A, L, P)
  python3 vim.command('let text = "%s"' % pyjoplin.run('complete_tag'))
  return text
endfunction

function! joplin#complete#note_tag(A, L, P)
  python3 vim.command('let text = "%s"' % pyjoplin.run('complete_note_tag'))
  return text
endfunction

function! joplin#complete#resource(A, L, P)
  python3 vim.command('let text = "%s"' % pyjoplin.run('complete_resource'))
  return text
endfunction

function! joplin#complete#note(A, L, P)
  python3 vim.command('let text = "%s"' % pyjoplin.run('complete_note', arg_lead=vim.eval('a:A')))
  return text
endfunction

function! joplin#complete#folder(A, L, P)
  python3 vim.command('let text = "%s"' % pyjoplin.run('complete_folder', arg_lead=vim.eval('a:A')))
  return text
endfunction
