git --no-pager diff --exit-code HEAD || begin
    set commit_message (gd HEAD | llm 'generate commit message from output of git diff. If there is no output, answer with empty message. Answer with just the commit message. Mention each area of work on a separate line.' | string collect)
    set diff_with_comments (git diff HEAD | sed 's/^/# /' | string collect)
    printf "%s\n\n%s\n" "$commit_message" "$diff_with_comments" | gcam -e
end; and gp
