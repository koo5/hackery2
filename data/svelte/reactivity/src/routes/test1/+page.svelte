<script>

    import {onMount} from "svelte";

    let numbers = Array(10).fill(0).map((_, i) => i);
    let my_numbers = $state(numbers);

    onMount(() => {
        console.log('Page mounted');
        setInterval(() => {
            console.log('numbers: ', numbers);
            my_numbers = my_numbers.map(n => n + 1);
        }, 1000);
    });



</script>

<h1>Page</h1>

{#each my_numbers as number}
    <p>{number}</p>
{/each}
