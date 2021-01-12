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

hi default JoplinPopup ctermfg=12 ctermbg=0 guibg=Magenta
hi default MenuItemIndicator term=bold cterm=underline

function! s:CompleteFunc(wordsfunc, var, A)
  exec printf("python3 pyjoplin.run('words2bvar', wordsfunc='%s', var='%s')", a:wordsfunc, a:var)
  let words = get(b:, a:var, [])
  call filter(words, printf('v:val =~ "^".a:A'))
  call filter(words, 'count(words, v:val) == 1')
  return words
endfunction

function! JoplinAllTagComplete(A, L, P)
  return <SID>CompleteFunc('all_tag_titles', 'all_tag_titles', a:A)
endfunction

function! JoplinNoteTagComplete(A, L, P)
  return <SID>CompleteFunc('note_tag_titles', 'note_tag_titles', a:A)
endfunction

function! JoplinAllResourceComplete(A, L, P)
  return <SID>CompleteFunc('all_resource_titles', 'all_resource_titles', a:A)
endfunction

function! JoplinNoteComplete(A, L, P)
  let var = 'note_complete_word'
  exec printf("python3 pyjoplin.run('note_match_text', arg_lead='%s', var='%s')", a:A, var)
  let text = get(b:, var, '')
  return text
endfunction

command! -nargs=0 JoplinWinOpen call joplin#open()
command! -nargs=0 JoplinWinClose call joplin#close()
command! -nargs=0 Joplin call joplin#toggle()
command! -nargs=1 -complete=custom,joplin#joplin_folder_complete JoplinSaveAsNote call joplin#saveas(0, <q-args>)
command! -nargs=1 -complete=custom,joplin#joplin_folder_complete JoplinSaveAsTodo call joplin#saveas(1, <q-args>)
command! -nargs=1 JoplinSearch call joplin#search(<q-args>)

augroup joplin_init
  autocmd!
  autocmd BufEnter tree.joplin let b:saved_prev_winnr = winnr('#')
  autocmd BufLeave tree.joplin let b:saved_last_line = line('.')
augroup end
