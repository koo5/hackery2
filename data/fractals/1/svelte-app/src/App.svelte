<script>
    import Fractal from './Fractal.svelte';
	let iterations = 7;
</script>

<main>
    <label>
    iterations:
        <input type=number bind:value={iterations} min=0 max=1000 step="1">
        <input type=range bind:value={iterations} min=0 max=1000 step="1">
    </label>
    <Fractal iterations={iterations}></Fractal>
</main>

