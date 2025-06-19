from flask import Flask, request, jsonify, send_from_directory, Response
import json
import os
import matplotlib.pyplot as plt
import numpy as np
import uuid
import torch
from datetime import datetime
import glob
from train import ComplexFingerprintClassifier, INPUT_SIZE, HIDDEN_SIZE, MODELS_DIR
from collect import WEBSITES
from advanced_data_converter import AdvancedDataConverter

app = Flask(__name__)

# Folder to save generated heatmaps
HEATMAP_DIR = os.path.join("static", "heatmaps")
os.makedirs(HEATMAP_DIR, exist_ok=True)

# Global variables for model and data conversion
loaded_model = None
model_info = {
    "loaded": False,
    "model_path": None,
    "loaded_at": None,
    "accuracy": None
}
advanced_converter = AdvancedDataConverter(input_size=INPUT_SIZE)

def load_latest_model():
    """Load the latest complex fingerprint classifier model"""
    global loaded_model, model_info
    
    try:
        model_pattern = os.path.join(MODELS_DIR, "complex_fingerprint_classifier*.pth")
        model_files = glob.glob(model_pattern)
        
        if not model_files:
            return False, "No complex model found"
        
        # Get the latest model file
        latest_model = max(model_files, key=os.path.getmtime)
        
        # Load model
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = ComplexFingerprintClassifier(INPUT_SIZE, HIDDEN_SIZE, len(WEBSITES))
        
        checkpoint = torch.load(latest_model, map_location=device)
        if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
            accuracy = checkpoint.get('accuracy', 'Unknown')
        else:
            model.load_state_dict(checkpoint)
            accuracy = 'Unknown'
        
        model.eval()
        loaded_model = model
        
        model_info = {
            "loaded": True,
            "model_path": latest_model,
            "loaded_at": datetime.now().isoformat(),
            "accuracy": accuracy,
            "device": str(device)
        }
        
        return True, f"Model loaded successfully: {os.path.basename(latest_model)}"
        
    except Exception as e:
        loaded_model = None
        model_info["loaded"] = False
        return False, f"Error loading model: {str(e)}"

def preprocess_trace(trace):
    """Preprocess trace for prediction (same as training)"""
    if len(trace) != INPUT_SIZE:
        return None
    
    trace_array = np.array(trace, dtype=np.float32)
    # Normalize (standard score)
    mean = trace_array.mean()
    std = trace_array.std()
    if std > 1e-6:
        trace_array = (trace_array - mean) / std
    
    return trace_array

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
        
        # Check if this is advanced trace data (dict with attacks) or simple trace data (list)
        if isinstance(trace, dict) and 'attacks' in trace:
            print("Received advanced trace data with attacks:", list(trace.get('attacks', {}).keys()))
            
            # Convert advanced trace to feature vector using AdvancedDataConverter
            try:
                feature_vector = advanced_converter.convert_advanced_trace(trace)
                trace_array = feature_vector.reshape(1, -1)
                print(f"Converted to feature vector of size: {feature_vector.shape}")
                print(f"Feature vector range: min={np.min(feature_vector):.2f}, max={np.max(feature_vector):.2f}")
            except Exception as e:
                print(f"Error converting advanced trace: {e}")
                return jsonify({"error": f"Failed to convert advanced trace: {str(e)}"}), 400
                
        elif isinstance(trace, list):
            print("Received simple trace:", len(trace), "samples")
            if not trace:
                return jsonify({"error": "Empty trace data"}), 400
            trace_array = np.array(trace).reshape(1, -1)
            
        else:
            return jsonify({"error": "Invalid trace data format"}), 400

        stored_traces.append(trace)

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

@app.route('/api/model/status', methods=['GET'])
def get_model_status():
    """Get current model status"""
    return jsonify(model_info)

@app.route('/api/model/reload', methods=['POST'])
def reload_model():
    """Reload the latest model"""
    success, message = load_latest_model()
    return jsonify({
        "success": success,
        "message": message,
        "model_info": model_info
    })

@app.route('/api/predict', methods=['POST'])
def predict_website():
    """Predict website from trace data"""
    try:
        if not loaded_model:
            return jsonify({"error": "No model loaded"}), 400
        
        data = request.get_json()
        trace = data.get('trace')
        
        # Handle both simple traces and advanced traces
        if isinstance(trace, dict) and 'attacks' in trace:
            print("Received advanced trace for prediction")
            # Convert advanced trace to feature vector
            try:
                processed_trace = advanced_converter.convert_advanced_trace(trace)
                print(f"Converted advanced trace to feature vector of size: {processed_trace.shape}")
            except Exception as e:
                print(f"Error converting advanced trace for prediction: {e}")
                return jsonify({"error": f"Failed to convert advanced trace: {str(e)}"}), 400
                
        elif isinstance(trace, list):
            print("Received simple trace for prediction")
            # Preprocess simple trace
            processed_trace = preprocess_trace(trace)
            if processed_trace is None:
                return jsonify({"error": f"Trace must be exactly {INPUT_SIZE} samples"}), 400
        else:
            return jsonify({"error": "Invalid trace data format"}), 400
        
        # Make prediction
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        loaded_model.to(device)
        
        with torch.no_grad():
            trace_tensor = torch.FloatTensor(processed_trace).unsqueeze(0).to(device)
            outputs = loaded_model(trace_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            
            predicted_class = torch.argmax(outputs, dim=1).item()
            confidence = probabilities[0][predicted_class].item()
            
            # Get all probabilities
            all_probs = probabilities[0].cpu().numpy()
        
        result = {
            "predicted_website": WEBSITES[predicted_class],
            "predicted_index": predicted_class,
            "confidence": float(confidence),
            "all_probabilities": {
                WEBSITES[i]: float(all_probs[i]) for i in range(len(WEBSITES))
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        print("Error in prediction:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/api/realtime/start', methods=['POST'])
def start_realtime_test():
    """Start real-time testing - returns instructions"""
    if not loaded_model:
        return jsonify({"error": "No model loaded"}), 400
    
    instructions = {
        "message": "Real-time testing ready",
        "instructions": [
            "1. Navigate to one of the target websites in a new tab:",
            f"   - {WEBSITES[0]}",
            f"   - {WEBSITES[1]}",
            f"   - {WEBSITES[2]}",
            "2. The side-channel trace will be automatically collected",
            "3. Click 'Predict Current Website' to get the prediction"
        ],
        "websites": WEBSITES,
        "model_info": model_info
    }
    
    return jsonify(instructions)

# Load model on startup
load_latest_model()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
