function dvr --wraps='docker volume remove' --description 'alias dvr docker volume remove'
  docker volume remove $argv
        
end
