function! joplin#statusline#note()
  let name = get(b:, 'joplin_path', '')
  if name == ''
    let name = bufname()
  endif
  return name
endfunction

function! joplin#statusline#airline(...)
  if &filetype == 'joplin.markdown'
    let w:airline_section_c = '%{joplin#statusline#note()}%m'
  elseif &filetype == 'joplin'
    let w:airline_section_c = ''
  endif
endfunction

function! joplin#statusline#refresh()
  if exists(':AirlineRefresh')
    AirlineRefresh
  endif
endfunction
