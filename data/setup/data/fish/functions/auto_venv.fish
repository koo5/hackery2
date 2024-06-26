function __auto_source_venv --on-variable PWD --description "Activate/Deactivate virtualenv on directory change"
  status --is-command-substitution; and return

  set maybe_env (pwd)/venv
  #echo $maybe_env


  if test "$VIRTUAL_ENV" != $maybe_env
    if functions --query deactivate
      deactivate
    end
    if test -e "$maybe_env/bin/activate.fish"
      source $maybe_env/bin/activate.fish
    end
  end

end
