/* Find the cache line size by running `getconf -a | grep CACHE` */
const LINESIZE = 64;
/* Find the L3 size by running `getconf -a | grep CACHE` */
const LLCSIZE = 4 * 1024 * 1024; 
/* Collect traces for 10 seconds; you can vary this */
const TIME = 10000;
/* Collect traces every 10ms; you can vary this */
const P = 10; 

function sweep(P) {
    const buffer = new Uint8Array(LLCSIZE);
    const counts = [];
    const K = Math.floor(TIME / P); // number of time windows

    for (let i = 0; i < K; i++) {
        const start = performance.now();
        let sweepCount = 0;

        // Keep sweeping until P milliseconds have passed
        while ((performance.now() - start) < P) {
            for (let j = 0; j < LLCSIZE; j += LINESIZE) {
                buffer[j];
            }
            sweepCount++;
        }

        counts.push(sweepCount);
    }

    return counts;
}

self.addEventListener('message', function(e) {
    if (e.data === "start") {
        const trace = sweep(P);
        self.postMessage(trace);
    }
});
