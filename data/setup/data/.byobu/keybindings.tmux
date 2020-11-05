unbind-key -n C-a
set -g prefix ^A
set -g prefix2 ^A
bind a send-prefix

# Undo Byobu's Keybindings
unbind-key -n F1
unbind-key -n S-F1
unbind-key -n F2
unbind-key -n C-F2
unbind-key -n S-F2
unbind-key -n C-S-F2
unbind-key -n F3
unbind-key -n F4
unbind-key -n C-Up
unbind-key -n C-Down
unbind-key -n C-Left
unbind-key -n C-Right
unbind-key -n C-S-Left
unbind-key -n C-S-Right
unbind-key -n C-S-Up
unbind-key -n C-S-Down
unbind-key -n S-F3
unbind-key -n S-F4
unbind-key -n S-Up
unbind-key -n S-Down
unbind-key -n S-Left
unbind-key -n S-Right
unbind-key -n C-F3
unbind-key -n C-F4
unbind-key -n C-S-F3
unbind-key -n C-S-F4
unbind-key -n M-Up
unbind-key -n M-Down
unbind-key -n M-Left
unbind-key -n M-Right
unbind-key -n S-M-Up
unbind-key -n S-M-Down
unbind-key -n S-M-Left
unbind-key -n S-M-Right
unbind-key -n F5
unbind-key -n M-F5
unbind-key -n S-F5
unbind-key -n C-F5
unbind-key -n C-S-F5
unbind-key -n F6
unbind-key -n M-F6
unbind-key -n S-F6
unbind-key -n C-F6
unbind-key -n F7
unbind-key -n S-F7
unbind-key -n M-NPage
unbind-key -n M-PPage
unbind-key -n F8
unbind-key -n C-F8
unbind-key -n C-S-F8
unbind-key -n M-S-F8
unbind-key -n S-F8
unbind-key -n F9
unbind-key -n S-F9
unbind-key -n C-F9
unbind-key -n M-F11
unbind-key -n C-F11
unbind-key -n S-F11
bind-key -n S-F12 source $BYOBU_PREFIX/share/byobu/keybindings/f-keys.tmux \; display-message "Byobu F-keys: ENABLED"
unbind-key -n M-F12
unbind-key -n C-S-F12
unbind-key -n M-IC
unbind-key -n C-a

# Documented in: $BYOBU_PREFIX/share/doc/byobu/help.tmux.txt
bind-key -n F1 previous-window
bind-key -n S-F1 new-window -k -n help '$BYOBU_PAGER $BYOBU_PREFIX/share/doc/byobu/help.tmux.txt'
#bind-key -n F2 new-window \; rename-window "-"
bind-key -n C-F2 display-panes \; split-window -h
bind-key -n S-F2 display-panes \; split-window -v
bind-key -n C-S-F2 new-session
#bind-key -n F3 previous-window
bind-key -n F12 next-window
bind-key -n M-Left previous-window
bind-key -n M-Right next-window
bind-key -n M-Up switch-client -p
bind-key -n M-Down switch-client -n
bind-key -n S-F3 display-panes \; select-pane -t :.-
bind-key -n S-F4 display-panes \; select-pane -t :.+
#bind-key -n S-Up display-panes \; select-pane -U
#bind-key -n S-Down display-panes \; select-pane -D
#bind-key -n S-Left display-panes \; select-pane -L
#bind-key -n S-Right display-panes \; select-pane -R
bind-key -n C-F3 display-panes \; swap-pane -s :. -t :.- \; select-pane -t :.-
bind-key -n C-F4 display-panes \; swap-pane -s :. -t :.+ \; select-pane -t :.+
bind-key -n C-S-F3 swap-window -t :-1
bind-key -n C-S-F4 swap-window -t :+1
bind-key -n M-S-Up resize-pane -U
bind-key -n M-S-Down resize-pane -D
bind-key -n M-S-Left resize-pane -L
bind-key -n M-S-Right resize-pane -R
bind-key -n S-F5 source $BYOBU_PREFIX/share/byobu/profiles/tmuxrc
bind-key -n M-F5 run-shell '$BYOBU_PREFIX/lib/byobu/include/toggle-utf8' \; source $BYOBU_PREFIX/share/byobu/profiles/tmuxrc
bind-key -n S-F5 new-window -k "$BYOBU_PREFIX/lib/byobu/include/cycle-status" \; source $BYOBU_PREFIX/share/byobu/profiles/tmuxrc
bind-key -n C-F5 send-keys ". $BYOBU_PREFIX/bin/byobu-reconnect-sockets" \; send-keys Enter
bind-key -n C-S-F5 new-window -d "byobu-select-profile -r"
#bind-key -n F6 detach
bind-key -n M-F6 run-shell '$BYOBU_PREFIX/lib/byobu/include/tmux-detach-all-but-current-client'
bind-key -n S-F6 run-shell 'exec touch $BYOBU_RUN_DIR/no-logout' \; detach
bind-key -n C-F6 kill-pane
#bind-key -n F7 copy-mode
bind-key -n S-F7 capture-pane -S -32768 \; save-buffer "$BYOBU_RUN_DIR/printscreen" \; delete-buffer \; new-window -n "PRINTSCREEN" "view $BYOBU_RUN_DIR/printscreen"
bind-key -n M-NPage copy-mode \; send-keys NPage
bind-key -n M-PPage copy-mode \; send-keys PPage
#bind-key -n F8 command-prompt -p "(rename-window) " "rename-window '%%'"
bind-key -n C-F8 command-prompt -p "(rename-session) " "rename-session '%%'"
bind-key -n S-F8 next-layout
bind-key -n M-S-F8 new-window -k "byobu-layout restore; clear; $SHELL"
bind-key -n C-S-F8 command-prompt -p "Save byobu layout as:" "run-shell \"byobu-layout save '%%'\""
bind-key -n S-F9 new-window -k -n config byobu-config
#bind-key -n S-F9 command-prompt -p "Send command to all panes:" "run-shell \"$BYOBU_PREFIX/lib/byobu/include/tmux-send-command-to-all-panes '%%'\""
#bind-key -n C-F9 command-prompt -p "Send command to all windows:" "run-shell \"$BYOBU_PREFIX/lib/byobu/include/tmux-send-command-to-all-windows '%%'\""
bind-key -n M-F11 break-pane
bind-key -n C-F11 join-pane -h -s :. -t :-1
bind-key -n S-F11 resize-pane -Z
bind-key -n S-F12 source $BYOBU_PREFIX/share/byobu/keybindings/f-keys.tmux.disable \; display-message "Byobu F-keys: DISABLED"
bind-key -n C-S-F12 new-window $BYOBU_PREFIX/lib/byobu/include/mondrian
bind-key -n M-F12 source $BYOBU_PREFIX/share/byobu/keybindings/mouse.tmux.enable
bind-key -n M-IC paste-buffer

#bind-key -n C-a new-window -n "ctrl-a" "byobu-ctrl-a"
