import { Store, Query, Quad } from './store.ts';

export class Store {
    constructor() {
        this._store = new Store();
    }

    query(query: Query, transform: (quad: Quad) => any) {
        return
}
