function! joplin#statusline#joplin_markdown()
  let name = get(b:, 'joplin_path', '')
  if name == ''
    let name = bufname()
  endif
  return name
endfunction

function! joplin#statusline#joplin_markdown_airline(...)
  if &filetype == 'joplin.markdown'
    let w:airline_section_c = '%{joplin#statusline#joplin_markdown()}%m'
    let g:airline_variable_referenced_in_statusline = 'foo'
  endif
endfunction

function! joplin#statusline#refresh()
  if exists(':AirlineRefresh')
    AirlineRefresh
  endif
endfunction
