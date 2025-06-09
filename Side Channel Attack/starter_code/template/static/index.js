function app() {
  return {
    // Application state
    latencyResults: null,
    traceData: [],
    heatmaps: [],
    status: "",
    isCollecting: false,
    statusIsError: false,
    showingTraces: false,

    // Collect latency data using warmup.js worker
    async collectLatencyData() {
      this.isCollecting = true;
      this.status = "Collecting latency data...";
      this.latencyResults = null;
      this.statusIsError = false;
      this.showingTraces = false;

      try {
        const worker = new Worker("warmup.js");

        const results = await new Promise((resolve) => {
          worker.onmessage = (e) => resolve(e.data);
          worker.postMessage("start");
        });

        this.latencyResults = results;
        this.status = "Latency data collection complete!";
        worker.terminate();
      } catch (error) {
        console.error("Error collecting latency data:", error);
        this.status = `Error: ${error.message}`;
        this.statusIsError = true;
      } finally {
        this.isCollecting = false;
      }
    },

    // Collect trace data using worker.js and send to backend
    async collectTraceData() {
      this.isCollecting = true;
      this.status = "Collecting trace data...";
      this.statusIsError = false;
      this.showingTraces = true;

      try {
        const worker = new Worker("worker.js");

        const traceData = await new Promise((resolve) => {
          worker.onmessage = (e) => resolve(e.data);
          worker.postMessage("start");
        });

        worker.terminate();

        const response = await fetch("/collect_trace", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ trace: traceData }),
        });

        if (!response.ok) throw new Error("Failed to send trace to backend");

        const result = await response.json(); // { heatmap: "path/to/img" }

        this.traceData.push(traceData);
        // this.heatmaps.push(result.heatmap);
        this.heatmaps.push({
          src: result.heatmap,
          min: result.min,
          max: result.max,
          range: result.range,
          samples: result.samples
        });

        this.status = "Trace collected and heatmap generated!";
      } catch (error) {
        console.error("Error collecting trace:", error);
        this.status = `Error: ${error.message}`;
        this.statusIsError = true;
      } finally {
        this.isCollecting = false;
      }
    },

    // Download the trace data as a JSON file
    async downloadTraces() {
      try {
        const response = await fetch("/download_traces");
        if (!response.ok) throw new Error("Failed to fetch trace data");

        const data = await response.json();
        const blob = new Blob([JSON.stringify(data, null, 2)], {
          type: "application/json",
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "trace_data.json";
        a.click();
        URL.revokeObjectURL(url);

        this.status = "Downloaded trace data!";
      } catch (error) {
        console.error("Download error:", error);
        this.status = `Error: ${error.message}`;
        this.statusIsError = true;
      }
    },

    // Clear all results from backend and UI
    async clearResults() {
      try {
        const response = await fetch("/api/clear_results", { method: "POST" });
        if (!response.ok) throw new Error("Failed to clear results");

        this.traceData = [];
        this.heatmaps = [];
        this.latencyResults = null;
        this.status = "All results cleared.";
      } catch (error) {
        console.error("Clear error:", error);
        this.status = `Error: ${error.message}`;
        this.statusIsError = true;
      }
    },
  };
}
