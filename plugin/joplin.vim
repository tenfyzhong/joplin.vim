if v:version < 800
  echom 'Joplin needs vim 8.0+'
  finish
endif

if !has('pythonx')
  echom 'Joplin needs vim support pythonx, see :help pythonx'
  finish
endif

command JoplinOpen call joplin#open()
command JoplinClose call joplin#close()
command Joplin call joplin#toggle()

augroup joplin_init
  autocmd!
  autocmd BufEnter tree.joplin let b:saved_prev_winnr = winnr('#')
  autocmd BufLeave tree.joplin let b:saved_last_line = line('.')
augroup end
