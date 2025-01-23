if status is-interactive
  . $HOME/hackery2/setup/data/fish/functions/auto_venv.fish
  __auto_source_venv
  . $HOME/hackery2/setup/data/fish/functions/aaaa.fish

  abbr --add sa ssh-add
  abbr --add kw kwrite
  abbr --add untar tar -xvf
  abbr --add root sudo terminator

end


#starship init fish | source


