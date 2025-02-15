<script>

    import {rooms, add_message} from 'falcon.svelte.ts';


    let {room_id} = $props();

    let text;

</script>

<div class="message-bar">
    <input type="text" bind:value={text} />
    <button on:click={() => {add_message(room_id, text); text = '';}}>Send</button>
</div>
