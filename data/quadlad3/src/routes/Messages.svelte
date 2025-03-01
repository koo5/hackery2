<script>

    import { rooms } from 'falcon.svelte.ts';
    import {MESSAGE, ROOM} from "$lib/falcon.svelte.js";

    let {room_id}= $props();

    let messages = $derived.by(() => {
        let result = [];
        for let q of store.query_all([room_id, ROOM + '#message', null]){
            result.push({
                id: q.o,
                text: store.query([q.o, MESSAGE + '#text']),
                author: store.query([q.o, MESSAGE + '#author']),
            });
        }
        return result;
    });

    let messages = $derived

</script>

<div class="messages">
    {#each $messages as message}
        <div>
            {message.author}: {message.text}
        </div>
    {/each}
</div>
