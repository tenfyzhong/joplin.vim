# joplin.vim
This is a plugin for us to use [joplin.app](https://joplinapp.org/) in vim.  


# Dependence
1. vim 8.2
2. python3
3. joplin.app

# Install
- [vim-plug](https://github.com/junegunn/vim-plug)
```vim
Plug 'tenfyzhong/joplin.vim'
```

- Manual
```
git clone https://github.com/tenfyzhong/joplin.vim.git ~/.vim/bundle/joplin.vim
echo 'set rtp+=~/.vim/bundle/joplin.vim' >> ~/.vimrc
vim -c 'helptag ~/.vim/bundle/joplin.vim/doc' -c qa!
```


# Usage
Enable you joplin.app's web clipper service first (Setting->Web Clipper).
And then copy you authorization token in the setting page. Set the token to
`g:joplin_token` in you vimrc. After enable the service, it will listen on
port 41184 by default. This plugin will connect to the default port when the
plugin start. If your joplin.app listen on other port, you should set the port
to `g:joplin_port`

Run command `Joplin` or `JoplinWinOpen` to open the `tree.joplin` window. It 
contains all notebooks and notes. 
