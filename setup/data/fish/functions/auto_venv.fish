# Stop venv activate.fish/deactivate from redefining fish_prompt.
# mc (Midnight Commander) wraps fish_prompt to detect subshell readiness;
# deactivate's prompt restore clobbered that wrapper, making mc hang 10s on
# startup. The venv is shown by fish_prompt itself via $VIRTUAL_ENV instead.
set -gx VIRTUAL_ENV_DISABLE_PROMPT 1

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
