<script>

    import { switchAccount, active_account, messagesArray, conversationsArray } from './stores2.js';


    messagesArray.subscribe(value => {
        console.log('messagesArray changed', value);
    });

    function addMessage() {
        messagesArray.update(messages => {
            messages.push({ text: 'New message' + Math.random() });
            return messages;
        });
    }


/*
 import { md } from '../messages.js';
 let messagesArray;
 $: messagesArray = $md.messagesArray;
*/



</script>

active_account: { JSON.stringify($active_account) },
<br>
<button on:click={switchAccount}>Switch Account</button>
<br>


{#if $messagesArray}
 messages: { JSON.stringify($messagesArray) }
  <br>

<ul>
  {#each $messagesArray as message (message.text)}
    <li>{message.text}</li>
  {/each}
</ul>
  
{:else}
  no data, no messages
  
{/if}

<hr>

conversationsArray: { JSON.stringify($conversationsArray) }
<br>
{#if $conversationsArray}
  <br>
  <ul>
    {#each $conversationsArray as conversation (conversation.address)}
      <li>{conversation.address}</li>
    {/each}
  </ul>
{:else}
  no data, no conversations
{/if}
<hr>
<button on:click={addMessage}>Add Message</button>
