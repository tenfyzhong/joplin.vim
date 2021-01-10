function! joplin#popup#info_filter(winid, key)
  if a:key == 'q'
    call popup_close(a:winid)
  endif
  return 1
endfunction
