(setq debug-on-error t)

(rassq-delete-all 'text-mode auto-mode-alist)
;; dont change mode for .txt files


;; (load "~/.emacs.d/floobits/floobits.el")
;; https://github.com/tj64/outshine




(global-set-key (kbd "<f8>") 'previous-buffer)
(global-set-key (kbd "<f9>") 'next-buffer)





;;(setq org-export-in-background t)
;;(setq org-export-preserve-breaks t)
;;(setq org-export-with-creator nil)
;;(setq org-export-with-toc 2)
;;(setq org-publish-project-alist
;;           '(("org"
;;              :base-directory "~/logs/"
;;              :publishing-directory "~/logs/html"
;;              :section-numbers nil
;;              :with-toc t)))





;;(global-set-key "\C-cl" 'org-store-link)
;;(global-set-key "\C-ca" 'org-agenda)
;;(global-set-key "\C-cc" 'org-capture)
;;(global-set-key "\C-cb" 'org-iswitchb)






(set-display-table-slot standard-display-table 'wrap ?\ ) 
;;??



'(package-initialize)
'(require 'ergoemacs-mode)
'(setq ergoemacs-handle-ctl-c-or-ctl-x 'only-C-c-and-C-x)
'(setq ergoemacs-theme nil) ;; Uses Standard Ergoemacs keyboard theme
'(setq ergoemacs-keyboard-layout "us") ;; Assumes QWERTY keyboard layout
'(ergoemacs-mode 1)
;;??do we use this?



;;(load "~/.emacs.d/lisp/sr-speedbar/sr-speedbar.el")
;;(require 'sr-speedbar)
;;(global-set-key (kbd "<f6>") 'sr-speedbar-toggle)




(add-to-list 'load-path "~/.emacs.d/lisp/circe")

(require 'circe)
(require 'circe-lagmon)


(setq lui-time-stamp-only-when-changed-p t)

(setq lui-max-buffer-size 99999999999)

(load-file "~/editable-log-password")

(setq circe-network-options
      `(("Freenode"
         :nick "editable-koo"
         :sasl-username "sirdancealot"
         :sasl-password ,editable-log-password-freenode
         :tls false
         :use-tls false
         :channels ( "#autonomic-dev" "#autonomic"  "#emacs-circe" "#eulergui" "#lemonparty"
;;"#swig" "##AGI" "#nars" "#netention" "#emacs-circe" "#marpa" "#mycroft" "#proglangdesign" "#idni"
		))))

;;(setq circe-network-options (cons (append `("Freenode" :nick "editable-koo" :sasl-username "sirdancealot" :sasl-password) (cons editable-log-password-freenode `(:channels ( "#autonomic-dev" "#autonomic" "#netention" "#emacs-circe" "#marpa" "#mycroft" "#eulergui" "#swig")))) ()))

(require 'lui-autopaste)
(add-hook 'circe-channel-mode-hook 'enable-lui-autopaste)

(setq circe-format-server-topic "*** Topic change by {userhost}: {topic-diff}")

(add-hook 'circe-chat-mode-hook 'my-circe-prompt)
(defun my-circe-prompt ()
  (lui-set-prompt
   (concat (propertize (concat (buffer-name) ">")
                       'face 'circe-prompt-face)
           " ")))

(require 'circe-color-nicks)
(enable-circe-color-nicks)


(setq fill-column 766)
(setq lui-read-only-output-p nil)

(eval-after-load 'circe
  '(defun lui-irc-propertize (&rest args)))

(defun circe-network-connected-p (network)
  "Return non-nil if there's any Circe server-buffer whose
`circe-server-netwok' is NETWORK."
  (catch 'return
    (dolist (buffer (circe-server-buffers))
      (with-current-buffer buffer
        (if (string= network circe-server-network)
            (throw 'return t))))))

(defun circe-maybe-connect (network)
  "Connect to NETWORK, but ask user for confirmation if it's
already been connected to."
  (interactive "sNetwork: ")
  (if (or (not (circe-network-connected-p network))
          (y-or-n-p (format "Already connected to %s, reconnect?" network)))
      (circe network)))

(defun circ ()
  "Connect to IRC"
  (interactive)
  (circe-maybe-connect "Freenode")
  (circe-lagmon-mode)
)

(defun circ2 ()
"ffff"
(interactive)
    (save-current-buffer
     (dolist (buffer (buffer-list))
      (set-buffer buffer)
      (if (eq major-mode 'circe-channel-mode) (progn
          (let ((fn 
          
                ;;(if (string= circe-chat-target "#tukutuku") "~/logs/tukutuku.log"
                ;;(if (string= circe-chat-target "#atlas-project") "~/logs/atlas-project.log"
          	;;(if (string= circe-chat-target "#swig") "~/logs/swig.log.txt"
          	;;(if (string= circe-chat-target "#tau") "~/logs/tau.log" 
          	;;(if (string= circe-chat-target "#zennet") "~/secret/zennet.log" 
          	;;(if (string= circe-chat-target "#netention") "~/logs/netention.log.txt" 
          	;;(if (string= circe-chat-target "#lemonparty") "~/logs/lemonparty.log.txt" 
          	;;(if (string= circe-chat-target "#eulergui") "~/logs/eulergui.log.txt" 
          	;;(if (string= circe-chat-target "#proglangdesign") "~/logs/proglangdesign.log.txt" 
          	(if (string= circe-chat-target "#autonomic") "~/logs/AutoNomic.log.txt" 
          	(if (string= circe-chat-target "#autonomic-dev") "~/logs/AutoNomic-dev.log.txt" 
          	(if (string= circe-chat-target "#emacs-circe") "~/logs/emacs-circe.log.txt" 
          	;;(if (string= circe-chat-target "##collaborate") "~/logs/collaborate.log.txt" 
          	'f)))))

;;            (prin1 circe-chat-target)
            (if (and (not (eq fn 'f))(eq buffer-file-name nil) )  (progn
;;             (prin1 "yay")
             (let ((fn (expand-file-name fn)))
              (goto-char (point-min))
              (insert-file-contents fn)
              (set-visited-file-name fn)
              (auto-save-buffers-enhanced-saver-buffer)
             )
            ))
          )
    	))
)))



(setq
 lui-time-stamp-position 'left
 lui-fill-type nil
 lui-time-stamp-format "%m/%d %H:%M:%S")

(setq lui-highlight-keywords '("stoopkid" "koo{0-9}" "editable-log"))












(setq auto-save-default nil)

;;; auto-save-buffers-enhanced.el --- Automatically save buffers in a decent way
;; -*- coding: utf-8; mode:emacs-lisp -*-

;; Copyright (C) 2007 Kentaro Kuribayashi
;; Author: Kentaro Kuribayashi <kentarok@gmail.com>
;; Note  : auto-save-buffers-enhanced.el borrows main ideas and some
;;         codes written by Satoru Takabayashi and enhances original
;;         one. Thanks a lot!!!
;;         See http://0xcc.net/misc/auto-save/

;; This file is free software; you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published
;; by the Free Software Foundation; either version 2, or (at your
;; option) any later version.

;; This file is distributed in the hope that it will be useful, but
;; WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
;; General Public License for more details.

;; You should have received a copy of the GNU General Public License
;; along with GNU Emacs; see the file COPYING.  If not, write to the
;; Free Software Foundation, Inc., 59 Temple Place - Suite 330,
;; Boston, MA 02111-1307, USA.

;;; Commentary:

;; * Description
;;
;; Emacs's native auto-save feature simply
;; sucks. auto-save-buffers-enhanced.el provides such and other more
;; useful features which only require a few configurations to set up.
;;
;; auto-save-buffers-enhanced.el borrows main ideas and some codes
;; written by Satoru Takabayashi and enhances the original one. Thanks
;; a lot!!!
;;
;; See http://0xcc.net/misc/auto-save/
;;
;; * Usage
;;
;; Just simply put the code below into your .emacs:
;;
;;   (require 'auto-save-buffers-enhanced)
;;   (auto-save-buffers-enhanced t)
;;
;; You can explicitly set what kind of files should or should not be
;; auto-saved. Pass a list of regexps like below:
;;
;;   (setq auto-save-buffers-enhanced-include-regexps '(".+"))
;;   (setq auto-save-buffers-enhanced-exclude-regexps '("^not-save-file" "\\.ignore$"))
;;
;; If you want `auto-save-buffers-enhanced' to work only with the files under
;; the directories checked out from VCS such as CVS, Subversion, and
;; svk, put the code below into your .emacs:
;;
;;   ;; If you're using CVS or Subversion or git
;;   (require 'auto-save-buffers-enhanced)
;;   (auto-save-buffers-enhanced-include-only-checkout-path t)
;;   (auto-save-buffers-enhanced t)
;;
;;   ;; If you're using also svk
;;   (require 'auto-save-buffers-enhanced)
;;   (setq auto-save-buffers-enhanced-use-svk-flag t)
;;   (auto-save-buffers-enhanced-include-only-checkout-path t)
;;   (auto-save-buffers-enhanced t)
;;
;; You can toggle `auto-save-buffers-enhanced' activity to execute
;; `auto-save-buffers-enhanced-toggle-activity'. For convinience, you
;; might want to set keyboard shortcut of the command like below:
;;
;;   (global-set-key "\C-xas" 'auto-save-buffers-enhanced-toggle-activity)
;;
;; Make sure that you must reload the SVK checkout paths from your
;; configuration file such as `~/.svk/config', in which SVK stores the
;; information on checkout paths, by executing
;; `auto-save-buffers-reload-svk' after you check new files out from
;; your local repository. You can set a keyboard shortcut for it like
;; below:
;;
;;   (global-set-key "\C-xar" 'auto-save-buffers-enhanced-reload-svk)
;;
;; For more details about customizing, see the section below:
;;

;;; Change Log:

;; 2011-08-01:
;;  * added a feature; auto-save *scratch* buffer into file.
;;
;; 2008-03-14:
;;  * fixed a typo: s/activitiy/avtivity/
;;
;; 2008-02-22:
;;  * fixed a bug: auto-saving didn't work under unreasonable situation...
;;    (Thanks to typester)
;;
;; 2008-02-19:
;;  * added git support.
;;  * fixed a bug: this package didn't work with SVN and CVS if
;;    use-svk-flag is non-nil.
;;
;; 2007-12-10:
;;  * added a command, `auto-save-buffers-enhanced-reload-svk'.
;;    (Thanks to typester: http://unknownplace.org/memo/2007/12/10#e001)
;;
;; 2007-10-18:
;;  * initial release

;;; Code:

;;;; You can customize auto-save-buffers-enhanced via the variables below
;;;; -------------------------------------------------------------------------

(defvar auto-save-buffers-enhanced-interval 0.5
  "*Interval by the second.

For that time, `auto-save-buffers-enhanced-save-buffers' is in
idle")

(defvar auto-save-buffers-enhanced-include-regexps '(".+")
  "*List that contains regexps which match `buffer-file-name' to
be auto-saved.")

(defvar auto-save-buffers-enhanced-exclude-regexps nil
  "*List that contains regexps which match `buffer-file-name' not
to be auto-saved.")

(defvar auto-save-buffers-enhanced-use-svk-flag nil
  "*If non-nil, `auto-save-buffers-enhanced' recognizes you're using svk
not CVS or Subversion.")

(defvar auto-save-buffers-enhanced-svk-config-path "~/.svk/config"
  "*Path of the config file of svk, which is usually located in
~/.svk/config.")

(defvar auto-save-buffers-enhanced-quiet-save-p nil
  "*If non-nil, without 'Wrote <filename>' message.")

(defvar auto-save-buffers-enhanced-save-scratch-buffer-to-file-p nil
  "*If non-nil, *scratch* buffer will be saved into the file same
as other normal files.")

(defvar auto-save-buffers-enhanced-cooperate-elscreen-p nil
  "*If non-nil, insert scratch data to elscreen default window.")

(defvar auto-save-buffers-enhanced-file-related-with-scratch-buffer
  (expand-file-name "~/.scratch")
  "*File which scratch buffer to be save into.")

;;;; Imprementation Starts from Here...
;;;; -------------------------------------------------------------------------

(eval-when-compile
 (require 'cl))

(defvar auto-save-buffers-enhanced-activity-flag t
  "*If non-nil, `auto-save-buffers-enhanced' saves buffers.")

;;;###autoload
(defun auto-save-buffers-enhanced (flag)
  "If `flag' is non-nil, activate `auto-save-buffers-enhanced' and start
auto-saving."
  (when flag
    (run-at-time t 5 'auto-save-buffers-enhanced-save-buffers))
  (when auto-save-buffers-enhanced-save-scratch-buffer-to-file-p
    (add-hook 'after-init-hook 'auto-save-buffers-enhanced-scratch-read-after-init-hook))
  (when auto-save-buffers-enhanced-cooperate-elscreen-p
    (add-hook 'elscreen-create-hook 'auto-save-buffers-enhanced-cooperate-elscreen-default-window)))

(defun auto-save-buffers-enhanced-scratch-read-after-init-hook ()
  (let ((scratch-buf (get-buffer "*scratch*")))
    (when scratch-buf
      (with-current-buffer scratch-buf
        (erase-buffer)
        (insert-file-contents auto-save-buffers-enhanced-file-related-with-scratch-buffer)))))

(defalias 'auto-save-buffers-enhanced-cooperate-elscreen-default-window
  'auto-save-buffers-enhanced-scratch-read-after-init-hook)

;;;###autoload
(defun auto-save-buffers-enhanced-include-only-checkout-path (flag)
  "If `flag' is non-nil, `auto-save-buffers-enhanced' saves only
the directories under VCS."
  (when flag
    (progn
      (setq auto-save-buffers-enhanced-include-regexps nil)
      (when auto-save-buffers-enhanced-use-svk-flag
        (auto-save-buffers-enhanced-add-svk-checkout-path-into-include-regexps))
      (add-hook 'find-file-hook
                'auto-save-buffers-enhanced-add-checkout-path-into-include-regexps))))

;;;; Command
;;;; -------------------------------------------------------------------------

;;;###autoload
(defun auto-save-buffers-enhanced-toggle-activity ()
  "Toggle `auto-save-buffers-enhanced' activity"
  (interactive)
  (if auto-save-buffers-enhanced-activity-flag
      (setq auto-save-buffers-enhanced-activity-flag nil)
    (setq auto-save-buffers-enhanced-activity-flag t))
  (if auto-save-buffers-enhanced-activity-flag
      (message "auto-save-buffers-enhanced on")
    (message "auto-save-buffers-enhanced off")))

;;;###autoload
(defun auto-save-buffers-enhanced-reload-svk ()
  "Reload the checkout paths from SVK configuration file."
  (interactive)
  (auto-save-buffers-enhanced-add-svk-checkout-path-into-include-regexps)
  (message (format "Realoaded checkout paths from %s" auto-save-buffers-enhanced-svk-config-path)))

;;;; Main Function
;;;; -------------------------------------------------------------------------

;;;(defvar-local maybe-save-last '()) 
;;;http://www.gnu.org/software/emacs/manual/html_node/elisp/Creating-Buffer_002dLocal.html#Creating-Buffer_002dLocal
;;;http://www.gnu.org/software/emacs/manual/html_node/elisp/Plist-Access.html#Plist-Access
;;;http://www.gnu.org/software/emacs/manual/html_node/elisp/Buffer-Modification.html

(defun maybe-save-tail (limit)
	(if ( > (buffer-size) limit)
	  (write-region 
		(max 1 (- (buffer-size) (* limit 1024))) 
		(buffer-size) 
		(concat  buffer-file-name "-tail" (number-to-string limit) ".txt")
		)))
 
(defun maybe-save (idle)
  ;;;thx
  (circ2);;i would have been merging the circ2 function with this one, since you see theres a lot of overlap. was a great idea to just call circ2 from here, thanks
  ;;glad my suggestion was useful
  ;;hmm, enough elisp for today, dont you think?
  ;;since i wasnt planning on doing an all out assault on all things going on here, yeah.
  ;;But, i am curious to try to understand it, and, IF it starts to click, i can perhaps do interesting things.
  ;;ok great, look around ad ill try to answer any questions?
  ;;i will do. im off for a walk now. was fun working
  ;;yeah im craving a break as well
  ;;i will look around tonight and see what i see and try to make a few mental highlight, and ill be in tomorrow evening. if you're around, we can chat about what im thinking
  ;;ok cool, yeah i should be around tomorrow
  ;;if i wanted to download the code, git -
  ;;the home dir where the repo is isnt accessible by http, but lets see
  
    (save-current-buffer
     (dolist (buffer (buffer-list))
      (set-buffer buffer)
       (if (and buffer-file-name
               auto-save-buffers-enhanced-activity-flag
               (buffer-modified-p)
               (not buffer-read-only)
               (file-writable-p buffer-file-name))
               (progn
		 (if ( < (buffer-size) 20)
                    (auto-save-buffers-enhanced-saver-buffer)
                ;;;else
		    (progn
   			(if (> idle 60) (progn
			    (dolist (limit '(20 170)) (maybe-save-tail limit))
	                    (auto-save-buffers-enhanced-saver-buffer)
			))
    			    ;;;(500 1000 2000)
		    )
	        )
)))))


;;well theres a timer that calls this
;;enhanced?
;;i have no idea, thats all taken from ...i forgot the name
;;this is all it is, just checks if emacs was idle greater than 10, and if so, run maybe-save.
;;yeah
(defun auto-save-buffers-enhanced-save-buffers ()
  "Save buffers if `buffer-file-name' matches one of
`auto-save-buffers-enhanced-include-regexps' and doesn't match
`auto-save-buffers-enhanced-exclude-regexps'."
  '(message "tick")
  (let ((idle (cadr (current-idle-time))))
    (if (not (eq idle nil))
   (if (> idle  10)
	(maybe-save idle)))))

;;;; Internal Functions
;;;; -------------------------------------------------------------------------

(defun auto-save-buffers-enhanced-saver-buffer (&optional scratch-p)
  (cond
   (scratch-p
    (let
        ((content (buffer-string)))
      (with-temp-file
          auto-save-buffers-enhanced-file-related-with-scratch-buffer
        (insert content))
      (set-buffer-modified-p nil)))
   (auto-save-buffers-enhanced-quiet-save-p
    (auto-save-buffers-enhanced-quiet-save-buffer))
   (t (save-buffer))))

(defun auto-save-buffers-enhanced-quiet-save-buffer ()
  (fset 'original-write-region (symbol-function 'write-region))
  (flet
      ((write-region (start end filename &optional append visit lockname mustbenew)
                     (original-write-region start end filename append -1 lockname mustbenew))
       (message (format-string &rest args) t))
    (save-buffer)
    (set-buffer-modified-p nil)
    (clear-visited-file-modtime)))

(defun auto-save-buffers-enhanced-regexps-match-p (regexps string)
  (catch 'matched
    (dolist (regexp regexps)
      (if (string-match regexp string)
          (throw 'matched t)))))

(defun auto-save-buffers-enhanced-add-svk-checkout-path-into-include-regexps ()
  (save-current-buffer
    (find-file auto-save-buffers-enhanced-svk-config-path)
    (when (file-readable-p buffer-file-name)
      (toggle-read-only))
    (goto-char (point-min))
    (while (re-search-forward "^[\t ]+\\(\\(/[^\n]+\\)+\\):[ ]*$" nil t)
      (when (and (file-exists-p (match-string 1))
                 (not (memq (match-string 1) auto-save-buffers-enhanced-include-regexps)))
        (setq auto-save-buffers-enhanced-include-regexps
              (cons (concat "^" (regexp-quote (match-string 1)))
                    auto-save-buffers-enhanced-include-regexps))))
    (kill-buffer (current-buffer))))

(defun auto-save-buffers-enhanced-add-checkout-path-into-include-regexps ()
  (let ((current-dir default-directory)
        (checkout-path nil))
    (catch 'root
      (while t
        (if (or (file-exists-p ".svn")
                (file-exists-p ".cvs")
                (file-exists-p ".git"))
            (setq checkout-path (expand-file-name default-directory)))
        (cd "..")
        (when (equal "/" default-directory)
            (throw 'root t))))
    (when (and checkout-path
               (not (memq checkout-path auto-save-buffers-enhanced-include-regexps)))
      (setq auto-save-buffers-enhanced-include-regexps
            (cons (concat "^" (regexp-quote checkout-path))
                  auto-save-buffers-enhanced-include-regexps)))
    (cd current-dir)))

(provide 'auto-save-buffers-enhanced)

;;; auto-save-buffers-enhanced.el ends here

(auto-save-buffers-enhanced t)















(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(menu ((t nil))))
(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(circe-format-self-say "<{mynick}>{body}")
 '(org-agenda-files (quote ("~/logs/")))
 '(speedbar-default-position (quote right)))



(setq
 lui-time-stamp-format "%d.%m.%y %H:%M:%S")

(setq visible-bell t)

(circ)
