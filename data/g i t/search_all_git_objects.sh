text="functional language perhaps yields itself better to explaining"
echo $text
{
    git rev-list --objects --all --grep="$text"
    git rev-list --objects -g --no-walk --all --grep="$text"
    git rev-list --objects --no-walk --grep="$text" \
        $(git fsck --unreachable |
          grep '^unreachable commit' |
          cut -d' ' -f3)
} | sort | uniq
