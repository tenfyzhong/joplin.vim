let s:menu_filter_func = {
      \ 'a': 'menu_add',
      \ 'm': 'menu_move',
      \ 'd': 'menu_delete',
      \ 'c': 'menu_copy',
      \ }

function! joplin#popup#info_filter(winid, key)
  if a:key == 'q'
    call popup_close(a:winid)
  endif
  return 1
endfunction

function! joplin#popup#menu_filter(winid, key)
  if a:key == 'q'
    call popup_close(a:winid)
    return 1
  elseif a:key == 'x'
    return 1
  endif
  let funcname = get(s:menu_filter_func, a:key, '')
  if funcname != ''
    exec printf('py3 pyjoplin.treenode_cmd("%s")', funcname)
    call popup_close(a:winid)
    return 1
  endif
  return popup_filter_menu(a:winid, a:key)
endfunction

function! joplin#popup#menu_callback(winid, result)
  if a:result <= 0
    return
  endif
  exec printf('py3 pyjoplin.treenode_cmd("menu_callback", result=%d)', a:result)
endfunction
