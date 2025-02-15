<script>

    import { rooms } from 'falcon.svelte.ts';


    let {room_id}= $props();
    let messages = $derived(rooms.get(room_id).messages);

</script>

<div class="messages">
    {#each $messages as message}
        <div>
            {message.author}: {message.text}
        </div>
    {/each}
</div>
