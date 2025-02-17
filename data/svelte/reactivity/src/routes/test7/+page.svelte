<script>
    let total = 100;
    let spent = $state(0);
    let left = $state(total);

    $effect(() => {
        left = total - spent;
    });

    $effect(() => {
        spent = total - left;
    });
</script>

<label>
    <input type="range" bind:value={spent} max={total} />
    {spent}/{total} spent
</label>
<br/>
<label>
    <input type="range" bind:value={left} max={total} />
    {left}/{total} left
</label>