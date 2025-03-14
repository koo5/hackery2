
type Val = any;

class Quad {
    /* subject */
    s: Val;
    /* predicate/property/verb */
    p: Val;
    /* object */
    o: Val;
    /* unique identifier */
    q: Val;

    constructor(s, p, o, q) {
        this.s = s;
        this.p = p;
        this.o = o;
        this.q = q;
    }
}

/* big graphs are split into chunks, chunks are a unit of transmission and bookkeeping, transparent to the application.
* gotta figure out if a chunk needs an identifier.
*  */
class Chunk {
    offset: number;
    graph: Val;
    quads: Val[];
}



type IndexKey = Val | readonly [Val, Val] | readonly [Val, Val, Val] | readonly [Val, Val, Val, Val];
type IndexedQuads = Map<IndexKey, Quad | Quad[]>;

enum IndexItem {
    s,
    p,
    o,
    q
}

type IndexingStrategy = IndexItem | readonly [IndexItem, IndexItem] | readonly [IndexItem, IndexItem, IndexItem] | readonly [IndexItem, IndexItem, IndexItem, IndexItem];


class Store {
    /* bookkeeping */
    chunks: Chunk[];
    /* indexes/quads */
    iqs: Map<IndexingStrategy, IndexedQuads>;

    constructor() {
        this.mats = new MatMap();
        this.chunks = [];
        this.iqs = new Map();
        this._add_strategy(IndexItem.q);
    }

    _add_strategy(strategy: IndexingStrategy) {
        this.iqs.set(strategy, new Map());
        /* todo: iterate quads from existing strategies and add to new strategy */
    }

    add(s: Val, p: Val, o: Val, q: Val)
    {
        /* add a quad to the store. Add  */
        let quad = new Quad(s, p, o, q);
        let iqs = this.iqs.get(IndexItem.q);
        if (iqs === undefined) {
            throw new Error("index not found");
        }
        let key = quad.q;
        /* q's are unique, so this.iqs[[quad.q]] maps to a single quad */
        iqs.set(key, quad);
        /* todo add to local chunk? */
    }

    *_query(s: Val | null, p: Val | null, o: Val | null, q: Val | null) {
        let iqs = this.iqs.get(IndexItem.q);
        for (let [key, quad] of iqs) {
            if (s !== null && quad.s !== s) {
                continue;
            }
            if (p !== null && quad.p !== p) {
                continue;
            }
            if (o !== null && quad.o !== o) {
                continue;
            }
            if (q !== null && quad.q !== q) {
                continue;
            }
            yield quad;
        }
    }

    query(query: readonly [Val, Val, Val, Val], transform: (quad: Quad) => any) {
        return new Query(this, query, transform);
    }


}


/*
a query could be one of:
materialize (object)
construct (graph)
select (array of quads)
ask (boolean)
*/



type Query = tuple<Val, Val, Val, Val>;

class _Query {
    store: Store;
    query: any;

    constructor(store: Store, query: any, callback: any) {
        this.store = store;
        this.query = query;
        this.callback = callback;
    }

    value() {
        let result = this.store.query(this.query.s, this.query.p, this.query.o, this.query.q);
        return result;
    }

    subscribe(callback: any) {
        this.callback = callback;
        this.store.subscribe(() => {
            this.callback(this.value());
        }
    }
}
