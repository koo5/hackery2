<script type='js'>
    import {onMount} from "svelte";

    let timer = 0;
    onMount(() => {
        setInterval(() => {
            timer++;
            if (timer % 10 == 0)
                console.log(timer);
        }, 100);
    });

</script>

loaded {(timer / 10).toString()} seconds
