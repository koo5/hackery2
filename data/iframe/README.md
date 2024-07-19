experiment with 

```
var data = { foo: 'bar' }
var event = new CustomEvent('myCustomEvent', { detail: data })
window.parent.document.dispatchEvent(event)

parent:

window.document.addEventListener('myCustomEvent', handleEvent, false)
function handleEvent(e) {
  console.log(e.detail) // outputs: {foo: 'bar'}
}

PS: Of course, you can send events in opposite direction same way.

document.querySelector('#iframe_id').contentDocument.dispatchEvent(event)
```