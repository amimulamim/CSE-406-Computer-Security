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

    // Real-time prediction state
    modelStatus: { loaded: false, accuracy: null },
    reloadingModel: false,
    predicting: false,
    predictionResult: null,
    sidebarOpen: false,

    // Initialize the app
    async init() {
      await this.checkModelStatus();
    },

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

    // Collect advanced multi-channel trace data
    async collectAdvancedTraceData() {
      this.isCollecting = true;
      this.status = "Collecting advanced multi-channel trace data...";
      this.statusIsError = false;
      this.showingTraces = true;

      try {
        const worker = new Worker("advanced_worker.js");

        // Add timeout to prevent hanging
        const advancedTraceData = await Promise.race([
          new Promise((resolve) => {
            worker.onmessage = (e) => resolve(e.data);
            worker.postMessage("start");
          }),
          new Promise((_, reject) => 
            setTimeout(() => reject(new Error("Advanced trace collection timed out (30s)")), 30000)
          )
        ]);

        worker.terminate();

        const response = await fetch("/collect_trace", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ trace: advancedTraceData }),
        });

        if (!response.ok) throw new Error("Failed to send advanced trace to backend");

        const result = await response.json();

        this.traceData.push(advancedTraceData);
        this.heatmaps.push({
          src: result.heatmap,
          min: result.min,
          max: result.max,
          range: result.range,
          samples: result.samples
        });

        this.status = "Advanced multi-channel trace collected!";
      } catch (error) {
        console.error("Error collecting advanced trace:", error);
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

    // Real-time prediction methods
    async checkModelStatus() {
      try {
        const response = await fetch("/api/model/status");
        if (response.ok) {
          this.modelStatus = await response.json();
        }
      } catch (error) {
        console.error("Error checking model status:", error);
      }
    },

    async reloadModel() {
      this.reloadingModel = true;
      try {
        const response = await fetch("/api/model/reload", { method: "POST" });
        const result = await response.json();
        
        if (result.success) {
          this.modelStatus = result.model_info;
          this.status = result.message;
          this.statusIsError = false;
        } else {
          this.status = `Model reload failed: ${result.message}`;
          this.statusIsError = true;
        }
      } catch (error) {
        console.error("Error reloading model:", error);
        this.status = `Error reloading model: ${error.message}`;
        this.statusIsError = true;
      } finally {
        this.reloadingModel = false;
      }
    },

    async predictCurrentWebsite() {
      this.predicting = true;
      this.predictionResult = null;
      this.status = "Collecting side-channel trace for prediction...";
      this.statusIsError = false;

      try {
        // Collect a fresh trace using the advanced worker
        const worker = new Worker("advanced_worker.js");
        
        const traceData = await Promise.race([
          new Promise((resolve) => {
            worker.onmessage = (e) => resolve(e.data);
            worker.postMessage("start");
          }),
          new Promise((_, reject) => 
            setTimeout(() => reject(new Error("Trace collection timed out (30s)")), 30000)
          )
        ]);

        worker.terminate();

        // Send trace for prediction
        const response = await fetch("/api/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ trace: traceData }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Prediction failed");
        }

        this.predictionResult = await response.json();
        this.status = `Prediction complete! Website: ${this.predictionResult.predicted_website}`;
        
      } catch (error) {
        console.error("Error during prediction:", error);
        this.status = `Prediction error: ${error.message}`;
        this.statusIsError = true;
      } finally {
        this.predicting = false;
      }
    },

    async predictWithLegacyMethod() {
      this.predicting = true;
      this.predictionResult = null;
      this.status = "Collecting legacy side-channel trace for prediction...";
      this.statusIsError = false;

      try {
        // Collect a fresh trace using the legacy worker
        const worker = new Worker("worker.js");
        
        const traceData = await new Promise((resolve) => {
          worker.onmessage = (e) => resolve(e.data);
          worker.postMessage("start");
        });

        worker.terminate();

        // Send trace for prediction
        const response = await fetch("/api/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ trace: traceData }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Prediction failed");
        }

        this.predictionResult = await response.json();
        this.status = `Legacy prediction complete! Website: ${this.predictionResult.predicted_website}`;
        
      } catch (error) {
        console.error("Error during legacy prediction:", error);
        this.status = `Legacy prediction error: ${error.message}`;
        this.statusIsError = true;
      } finally {
        this.predicting = false;
      }
    },
  };
}
