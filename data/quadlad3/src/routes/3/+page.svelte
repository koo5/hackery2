<script>

    import Obj from './Obj.svelte';

    let obj = {a:0};

    let my_obj = $state(obj);

</script>

<h1>Page</h1>

<div class="page">

<Obj obj={my_obj} />

</div>
<style>
    .page {
        line-height: 0.8;
    }
    </style>
