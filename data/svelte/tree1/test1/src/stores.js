
=====



export let messagesArray = derived(md, ($md, set) => {
    console.log('messagesArray update, $md:', $md);
    if ($md) {
        set(get($md.messagesArray));
        $md.selected_conversation.subscribe(set);
    }
}, null);



