/* Find the cache line size by running `getconf -a | grep CACHE` */
const LINESIZE = 64;

function readNlines(n) {
  const bufferSize = n * LINESIZE;
  const buffer = new Uint8Array(bufferSize);
  const timings = [];

  for (let repeat = 0; repeat < 10; repeat++) {
    const start = performance.now();

    // Access every cache line
    for (let i = 0; i < bufferSize; i += LINESIZE) {
      buffer[i];
    }

    const end = performance.now();
    timings.push(end - start);
  }

  // Sort and return median
  timings.sort((a, b) => a - b);
  const mid = Math.floor(timings.length / 2);
  return timings.length % 2 === 0
    ? (timings[mid - 1] + timings[mid]) / 2
    : timings[mid];
}

self.addEventListener("message", function (e) {
  if (e.data === "start") {
    const results = {};

    const inputSizes = [
      1,
      10,
      100,
      1000,
      10000,
      100000,
      1000000,
      10000000,
    ];

    for (const n of inputSizes) {
      try {
        const medianTime = readNlines(n);
        results[n] = medianTime;
      } catch (err) {
        console.error("Failed for n =", n, err);
        break;
      }
    }

    self.postMessage(results);
  }
});
