if v:version < 800
  echom 'Joplin needs vim 8.0+'
  finish
endif

if !has('python3')
  echom 'Joplin needs vim support python3, see :help python3'
  finish
endif

if !exists('g:joplin_token')
  echohl WarningMsg | echom "joplin.vim: Please set g:joplin_token first." | echohl None
  finish
endif

function! JoplinAllTagComplete(A, L, P)
  python3 pyjoplin.run('tag2bvar', tagfunc='all_tag_titles', var='tag_titles')
  let tag_titles = get(b:, 'tag_titles', [])
  call filter(tag_titles, printf('v:val =~ "^".a:A'))
  return tag_titles
endfunction

function! JoplinNoteTagComplete(A, L, P)
  python3 pyjoplin.run('tag2bvar', tagfunc='note_tag_titles', var='tag_titles')
  let tag_titles = get(b:, 'tag_titles', [])
  call filter(tag_titles, printf('v:val =~ "^".a:A'))
  return tag_titles
endfunction

command! JoplinOpen silent call joplin#open()
command! JoplinClose silent call joplin#close()
command! Joplin silent call joplin#toggle()

augroup joplin_init
  autocmd!
  autocmd BufEnter tree.joplin let b:saved_prev_winnr = winnr('#')
  autocmd BufLeave tree.joplin let b:saved_last_line = line('.')
augroup end
