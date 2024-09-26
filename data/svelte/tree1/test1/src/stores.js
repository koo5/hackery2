
export let accounts = writable([]);

export let active_account_store = writable(null);

export let active_account = derived(active_account_store, $active_account_store => {
    if ($active_account_store)
        return get($active_account_store);
    else
        return {};
})

active_account_store.subscribe(value => {
    // console.log('ACTIVE ACCOUNT:', value);
    console.log('ACTIVE ACCOUNT:', maybeGet(value));
});

function maybeGet(store) {
    if (store)
        return get(store);
}

export function module_data(module_id) {
    return derived(active_account_store, $active_account_store => {
        if (!$active_account_store)
            return null;
        let result = get($active_account_store).module_data[module_id];
        console.log('$active_account_store:', get($active_account_store));
        console.log('MODULE DATA:', result);
    });
}

export let md = module_data('messages');

md.subscribe(value => {
    console.log('MD: ', value);
};

export let messagesArray = derived(md, ($md, set) => {
    console.log('messagesArray update, $md:', $md);
    if ($md) {
        set(get($md.messagesArray));
        $md.selected_conversation.subscribe(set);
    }
}, null);



