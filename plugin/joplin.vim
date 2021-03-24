if exists('g:joplin_loaded')
  finish
endif
let g:joplin_loaded = 1

if v:version < 802
  echom 'Joplin needs vim 8.2+'
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

hi default JoplinInfoWin term=None cterm=None ctermfg=Cyan gui=None guifg=Cyan

command! -nargs=0 JoplinWinOpen call joplin#open()
command! -nargs=0 JoplinWinClose call joplin#close()
command! -nargs=0 Joplin call joplin#toggle()
command! -nargs=1 -complete=custom,joplin#complete#folder JoplinSaveAsNote call joplin#saveas(0, <q-args>)
command! -nargs=1 -complete=custom,joplin#complete#folder JoplinSaveAsTodo call joplin#saveas(1, <q-args>)
command! -nargs=1 JoplinSearch call joplin#search(<q-args>)

augroup joplin_init
  autocmd!
  autocmd BufEnter tree.joplin let b:saved_prev_winnr = winnr('#')
  autocmd BufLeave tree.joplin let b:saved_last_line = line('.')
augroup end
