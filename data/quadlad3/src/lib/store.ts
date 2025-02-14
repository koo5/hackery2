
type Val = any;
type Ref = number;
type ValMap = Map<Ref, Val>;

class Quad {
    /* subject */
    s: Ref;
    /* predicate/property/verb */
    p: Ref;
    /* object */
    o: Ref;
    /* unique identifier */
    q: Ref;

    constructor(s, p, o, q) {
        this.s = s;
        this.p = p;
        this.o = o;
        this.q = q;
    }
}

/* big graphs are split into chunks, chunks are a unit of transmission and bookkeeping, transparent to the application. */
class Chunk {
    offset: number;
    graph: Ref;
    quads: Ref[];
}


/* a map of domain-specific materializations */
type MatMap = Map<Ref, any>;


type IndexKey = Val | readonly [Val, Val] | readonly [Val, Val, Val] | readonly [Val, Val, Val, Val];
type IndexedQuads = Map<IndexKey, Quad[]>;

enum IndexItem {
    s,
    p,
    o,
    q
}

type IndexingStrategy = readonly [IndexItem] | readonly [IndexItem, IndexItem] | readonly [IndexItem, IndexItem, IndexItem] | readonly [IndexItem, IndexItem, IndexItem, IndexItem];

class Store {
    /* a Map of Materialization Maps.  */
    mats: MatMap;
    /* a Mapping from Refs to actual values.*/
    vals: ValMap;
    /* bookkeeping */
    chunks: Chunk[];
    /* indexes/quads */
    iqs: Map<IndexingStrategy, IndexedQuads>;

    constructor() {
        this.mats = new MatMap();
        this.vals = new Map();
        this.chunks = [];
        this.iqs = new Map();
    }

    /* if we want to support non-hashable values:

    add(s: any, p: any, o: any, q: any)
    {
        if (typeof s === 'object')
            let ref = this.add_ref(s);
            ....

    gc()
    {
        ...
    }
    */



     */

    add(s: Ref, p: Ref, o: Ref, q: Ref)
    /* add a quad to the store. Add  */
    {
        let quad = new Quad(s, p, o, q);
        let iqs = this.iqs[[quad.q]]
        if (iqs === undefined)
        {
            iqs = new Map();
            this.iqs[[quad.q]] = iqs;
        }
        let key = [quad.q];



}
