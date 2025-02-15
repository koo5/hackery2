<script>

    import {onMount} from "svelte";

    let numbers = [1, 2, 3, 4, 5];

    onMount(() => {
        console.log('Page mounted');
        setInterval(() => {
            numbers = numbers.map(n => n + 1);
        }, 1000);
    });

    let my_numbers = $state(numbers);

</script>

<h1>Page</h1>

{#each my_numbers as number}
    <p>{number}</p>
{/each}