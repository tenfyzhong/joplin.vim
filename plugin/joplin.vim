if !has('pythonx')
  finish
endif

if !exists('g:joplin_window_name')
  let g:joplin_window_name = 'tree.joplin'
endif

command JoplinOpen call joplin#open()
command JoplinClose call joplin#close()
command Joplin call joplin#toggle()

augroup joplin_init
  autocmd!
  autocmd BufEnter tree.joplin let b:saved_winnr = winnr('#')
augroup end
