<script>

    import Tree from "svelte-tree";
    import Stores from "./Stores.svelte";
    import PageReloadClock from "./PageReloadClock.svelte";
    
    export let name;



	const tree = [
        {
            name: "This is a root node",
            children: [
                {
                    name: "And it has",
                },
                {
                    name: "two children",
                },
            ],
        },
        {
            name: "This is another root node",
            children: [
                {
                    name: "This one is alone",
                },
                {
                    name: "But this one has nested children",
                    children: [
                        {
                            name: "Like this",
                        },
                        {
                            name: "and this",
                        },
                    ],
                },
            ],
        },
    ];
</script>

<main>

  <PageReloadClock/>
  <br>
  <Stores />
<hr>  
	<Tree {tree} let:node>
		<div class="name">{node.name}</div>
	</Tree>

</main>

<style>
	main {
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>
