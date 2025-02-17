import { createSubscriber } from 'svelte/reactivity';
import { on } from 'svelte/events';

const isSSR = typeof window === 'undefined';

export class MyMediaQuery {
    #query;
    #subscribe;

    constructor(query) {

        if (isSSR)
            return;

        this.#query = window.matchMedia(`(${query})`);

        this.#subscribe = createSubscriber((update) => {
            // when the `change` event occurs, re-run any effects that read `this.current`
            const off = on(this.#query, 'change', update);

            // stop listening when all the effects are destroyed
            return () => off();
        });
    }

    get current() {
        if (isSSR)
            return;
        this.#subscribe();

        // Return the current state of the query, whether or not we're in an effect
        return this.#query.matches;
    }
}
