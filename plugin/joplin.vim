if !has('pythonx')
  finish
endif

if !exists('g:tagbar_iconchars')
  if has('multi_byte') && has('unix') && &encoding ==# 'utf-8' &&
    \ (!exists('+termencoding') || empty(&termencoding) || &termencoding ==# 'utf-8')
    let g:joplin_iconchars = ['▶', '▼']
  else
    let g:joplin_iconchars = ['+', '-']
  endif
endif

command Joplin call joplin#open_window()
