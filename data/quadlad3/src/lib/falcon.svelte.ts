
import { Store } from "spoq/svelte";


let store = new Store();


let rooms = store.query(null, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "https://koo5.github.com/falcon/v0/falcon#room");




