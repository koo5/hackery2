
import { Store, Quad } from "svoq/svelte";

export let NAMESPACE = "https://koo5.github.com/falcon/v0/falcon";
export let RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#";
export let RDFS = "http://www.w3.org/2000/01/rdf-schema#";
export let ROOM = NAMESPACE + "/room";
export let MESSAGE = NAMESPACE + "/message";

let store = new Store();


export let rooms = store.query(null, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "https://koo5.github.com/falcon/v0/falcon#room");

export let add_room()
{
    let room_id = store.id(ROOM + '/');
    store.add(room_id, RDF + '#type', ROOM);
    return room_id;
}

