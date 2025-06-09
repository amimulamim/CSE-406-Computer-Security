from flask import Flask, request, jsonify, send_from_directory
import os
import matplotlib.pyplot as plt
import numpy as np
import uuid

app = Flask(__name__)

# Folder to save generated heatmaps
HEATMAP_DIR = os.path.join("static", "heatmaps")
os.makedirs(HEATMAP_DIR, exist_ok=True)

# In-memory storage
stored_traces = []
stored_heatmaps = []

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/collect_trace', methods=['POST'])
def collect_trace():
    """
    Receive trace data and generate heatmap.
    1. Receive trace as JSON list.
    2. Generate heatmap using matplotlib.
    3. Save and return heatmap path.
    """
    try:
        data = request.get_json()
        trace = data.get('trace')

        if not trace or not isinstance(trace, list):
            return jsonify({"error": "Invalid trace data"}), 400

        # Store the trace
        stored_traces.append(trace)

        # Generate heatmap (1-row)
        trace_array = np.array(trace).reshape(1, -1)
        fig, ax = plt.subplots(figsize=(12, 1.5))
        heatmap = ax.imshow(trace_array, cmap='hot', aspect='auto')
        ax.axis('off')

        # Save image
        filename = f"heatmap_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(HEATMAP_DIR, filename)
        plt.savefig(filepath, bbox_inches='tight', pad_inches=0.1)
        plt.close(fig)

        heatmap_url = f"/static/heatmaps/{filename}"
        stored_heatmaps.append(heatmap_url)

        return jsonify({"heatmap": heatmap_url})

    except Exception as e:
        print("Error in /collect_trace:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/api/clear_results', methods=['POST'])
def clear_results():
    """
    Clears stored traces and deletes heatmap images.
    """
    try:
        stored_traces.clear()
        for path in stored_heatmaps:
            fname = os.path.basename(path)
            fpath = os.path.join(HEATMAP_DIR, fname)
            if os.path.exists(fpath):
                os.remove(fpath)
        stored_heatmaps.clear()

        return jsonify({"status": "success", "message": "All traces and heatmaps cleared."})

    except Exception as e:
        print("Error clearing results:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
