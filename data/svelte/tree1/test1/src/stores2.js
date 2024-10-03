import {derived, writable, get } from "svelte/store";

import { arr } from "./test.js";

console.log('arr:', JSON.stringify(arr));

arr.push('hello');

console.log('arr:', JSON.stringify(arr));

export let accounts = writable([
    writable({id:0, module_data: {messages: {
        messagesArray: writable([{text: 'ahoj'},{text: 'mami'}]),
                conversationsArray: writable([{address:"mamka"}, {address:"tatka"}]),
            }}}),
    writable({id:1, module_data: {messages: {
        messagesArray: writable([{text: 'cau'},{text: 'vole'}]),
                conversationsArray: writable([{address:"nakej otrapa"}, {address:"jinej otrapa"}]),
            }}}),
]);

let active_account_id = null;


export function switchAccount() {
    if (active_account_id === null)
        active_account_id = 0;
    else if (active_account_id === 0)
        active_account_id = 1;
    else
        active_account_id = null;
    active_account_store.set(get(accounts)[active_account_id]);
}
    
export let active_account_store = writable(null);

export let active_account = derived(active_account_store, $active_account_store => {
    if ($active_account_store)
        return get($active_account_store);
    else
        return {note: 'no account is active'};
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
        if (!$active_account_store) {
            console.log('no active account');
            return null;
        }
        let result = get($active_account_store).module_data[module_id];
        console.log('$active_account_store:', get($active_account_store));
        console.log('MODULE DATA:', result);
        return result;
    });
}

export let md = module_data('messages');

md.subscribe(v => {
    console.log('MD: ', v);
});




/// ============


export let messagesArray = writable([]);
let messagesArrayset = messagesArray.set;

md.subscribe(value => {
    console.log('MD: ', value);
    if (value) {
        messagesArrayset(get(value.messagesArray));
    }
    else {
        messagesArrayset([]);
    }
})

messagesArray.set = (v) => {
    get(active_account)?.module_data.messagesArray.set(v);
};

messagesArray.subscribe(v => {
    console.log('messagesArray:', v);
});


export function relay(data_name) {
    let result = writable();
    let setter = result.set;

    md.subscribe(value => {
        console.log('MD: ', value);
        if (value) {
            setter(get(value[data_name]));
        } else {
            setter(null);
        }
    });

    result.set = (v) => {
        get(active_account)?.module_data[data_name].set(v);
    };
    result.subscribe(v => {
        console.log(data_name, ':', v);
    });
    return result;
}

export let conversationsArray = relay('conversationsArray');


/// ============


/*
export let conversationsArray = derived(md, ($md, set) => {
    console.log('messagesArray update, $md:', $md);
    if ($md) {
        set(get($md.conversationsArray));
        if($md.conversationsArray)
            $md.conversationsArray.subscribe(set);
    }
}, null);
*/


