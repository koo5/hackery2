<script>

    import {switchAccount, active_account, messagesArray} from './stores2.js';


    messagesArray.subscribe(value => {
        console.log('messagesArray changed', value);
    });

</script>

active_account: { JSON.stringify($active_account) },
<br>
<button on:click={switchAccount}>Switch Account</button>
<br>


{#if $messagesArray}
 messages: { JSON.stringify($messagesArray) }
{:else}
  no data, no messages
  
{/if}
