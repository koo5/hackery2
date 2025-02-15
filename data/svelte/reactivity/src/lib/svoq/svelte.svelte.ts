import { Store, Query } from './store.ts';


class Store {
    constructor() {
        this._store = new Store();
    }

    query(query: Query, transform: (quad: Quad) => any) {
        return
}
