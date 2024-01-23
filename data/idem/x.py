import augeas

aug = augeas.Augeas()
aug.set('/files/etc/sysctl.conf/fs.inotify.max_inotify_watches', '44194305')
aug.set('/files/etc/sysctl.conf/fs.inotify.max_user_watches', '44194305')
aug.save()
