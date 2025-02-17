<script>

    import Obj from './Obj.svelte';

    let obj = {a:0};

    let my_obj = $state(obj);

</script>


<div class="page">

{JSON.stringify(my_obj)}

<h1>Page</h1>


    <Obj obj={my_obj} />

</div>

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>

<style>
    .page {
        line-height: 0.8;
    }
</style>
