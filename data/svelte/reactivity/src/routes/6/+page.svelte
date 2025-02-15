<script>

    let todos = $state([
        {
            done: false,
            text: 'add more todos'
        }
    ]);


    function test() {
        console.log('test');
        let { done, text } = todos[0];
        todos[0].done = !todos[0].done;
    }


</script>


{#each todos as todo}
    <div>
        <input type="checkbox" bind:checked={todo.done}>
        <input type="text" bind:value={todo.text}>
    </div>
{/each}

<button onclick={() => todos.push({done: false, text: ''})}>add todo</button>
<button onclick={() => test()}>test</button>
