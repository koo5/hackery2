
type Val = any;
type Ref = number;
type ValMap = Map<Ref, Val>;

class Quad {
    /* subject */
    s: Ref;
    /* predicate */
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
    mmm: Map<Ref, MatMap>(),
    /* a Mapping from Refs to actual values.*/
    vals: ValMap;
    /* bookkeeping */
    chunks: Chunk[];
    /* indexes/quads */
    iqs: Map<IndexingStrategy, IndexedQuads>;

    gc() {
        let vals_clean = new ValMap();
        for (let [_, v: Quad] of this.iqs[[q]])
            vals_clean.set(v.s, this.vals.get(v.s));
            vals_clean.set(v.p, this.vals.get(v.p));
            vals_clean.set(v.o, this.vals.get(v.o));
            vals_clean.set(v.q, this.vals.get(v.q));
        }
        this.vals = vals_clean;
    }

}



let app = $state({

});
