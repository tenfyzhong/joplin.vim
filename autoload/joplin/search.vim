function! joplin#search#quickfixtext(info)
  let items = getqflist({'id': a:info.id, 'items': 1}).items
  let line = []
  for idx in range(a:info.start_idx-1, a:info.end_idx-1)
    call add(line, items[idx].text)
  endfor
  return line
endfunction
