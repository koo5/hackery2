<script>
    let total = 100;
    let spent = $state(0);
    let left = $state(total);

    function updateSpent(e) {
        spent = +e.target.value;
        left = total - spent;
    }

    function updateLeft(e) {
        left = +e.target.value;
        spent = total - left;
    }
</script>

<label>
    <input type="range" value={spent} oninput={updateSpent} max={total} />
    {spent}/{total} spent
</label>
<br/>
<label>
    <input type="range" value={left} oninput={updateLeft} max={total} />
    {left}/{total} left
</label>
