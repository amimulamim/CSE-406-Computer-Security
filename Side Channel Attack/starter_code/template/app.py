from flask import Flask, request, jsonify, send_from_directory, Response
import json
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
    try:
        data = request.get_json()
        trace = data.get('trace')
        print("Received trace:", trace[:10], "...", len(trace), "samples")


        if not trace or not isinstance(trace, list):
            return jsonify({"error": "Invalid trace data"}), 400

        stored_traces.append(trace)

        trace_array = np.array(trace).reshape(1, -1)

        # Calculate metadata
        min_val = int(np.min(trace_array))
        max_val = int(np.max(trace_array))
        range_val = int(max_val - min_val)
        samples = int(trace_array.shape[1])

        filename = f"heatmap_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(HEATMAP_DIR, filename)

        # Generate heatmap


        fig, ax = plt.subplots(figsize=(24, 2))  # Wider figure
        ax.imshow(trace_array, cmap='plasma', aspect='auto')
        ax.axis('off')

        # Save without tight layout cropping
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        plt.savefig(filepath, dpi=200, bbox_inches='tight', pad_inches=0.01)




        plt.close(fig)

        heatmap_url = f"/static/heatmaps/{filename}"
        stored_heatmaps.append(heatmap_url)

        return jsonify({
            "heatmap": heatmap_url,
            "min": min_val,
            "max": max_val,
            "range": range_val,
            "samples": samples
        })

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


@app.route('/download_traces', methods=['GET'])
def download_traces():
    json_data = json.dumps(stored_traces, indent=2)
    return Response(
        json_data,
        mimetype='application/json',
        headers={"Content-Disposition": "attachment;filename=traces.json"}
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
