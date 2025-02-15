<script>

    import { rooms, add_room } from 'falcon.svelte.ts';
    import Messages from './Messages.svelte';
    import MessageBar from './MessageBar.svelte';

    let room_id = $state();
    let room = $derived(rooms.get(room_id));


</script>


<div class="content">

    <div class="sidebar">

        <ul>
            {#each $rooms as room}
                <li>

                    <div onclick={room_id = room.id}>
                        {room.name}
                    </div>

                </li>
            {/each}
        </ul>
        <button on:click={() => {room_id = add_room()}>Add Room</button>

    </div>

    <div class="main">

        <h1>Room {room_id}</h1>

        <Messages room_id={room_id} />

        <MessageBar room_id={room_id} />

    </div>
</div>