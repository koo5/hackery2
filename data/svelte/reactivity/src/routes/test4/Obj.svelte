<script>

    let { obj } = $props();

    $effect(() => {
        const interval = setInterval(() => {
            if (obj['a'] === undefined) obj['a'] = 0;
            obj['a']++;
            let key = obj['a'];
            if (key > 1) clearInterval(interval);
            obj['b'+key] = {};
        }, 1000);

        return () => {
            clearInterval(interval);
        };
    });


</script>
{#each Object.keys(obj) as key}
    {#if typeof obj[key] === 'object'}
        {key}: <svelte:self obj={obj[key]} />
    {:else}
        {key}: {obj[key]}
    {/if}
    |
{/each}
