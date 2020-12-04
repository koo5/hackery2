```

This is normally set by the secure_path option in /etc/sudoers. From man sudoers:

 secure_path   Path used for every command run from sudo.  If you don't
               trust the people running sudo to have a sane PATH environ‐
               ment variable you may want to use this.  Another use is if
               you want to have the “root path” be separate from the “user
               path”.  Users in the group specified by the exempt_group
               option are not affected by secure_path.  This option is not
               set by default.


```