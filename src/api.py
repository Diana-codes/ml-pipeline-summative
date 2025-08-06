import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1' # Force TensorFlow to use CPU

# Ensure all necessary Flask components are imported, including send_from_directory
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import shutil
import tempfile
from flask_cors import CORS
import numpy as np # Import numpy with alias 'np'
from PIL import Image # Import Image from Pillow

# Import functions from our src modules
from src.preprocessing import preprocess_single_image, load_and_preprocess_bulk_data, create_data_generator
from src.model import create_cnn_model, train_model
from src.prediction import load_ml_model, predict_image

app = Flask(__name__)
CORS(app)

# --- START OF CHANGES ---
# Define project root and build all paths relative to it
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'uploads')
RETRAIN_DATA_FOLDER = os.path.join(PROJECT_ROOT, 'retrain_data')
MODEL_PATH = os.path.join(PROJECT_ROOT, 'models', 'image_classifier_model.h5')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
# --- END OF CHANGES ---

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'zip'}

# Ensure all necessary directories exist at startup
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RETRAIN_DATA_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True) # Ensure models directory exists
os.makedirs(os.path.join(DATA_DIR, 'train'), exist_ok=True) # Ensure data/train dir exists for insights
os.makedirs(os.path.join(DATA_DIR, 'test'), exist_ok=True) # Ensure data/test dir exists for insights


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return "ML Pipeline API is running!"

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        try:
            preprocessed_image = preprocess_single_image(filepath)
            prediction_result = predict_image(preprocessed_image)
            return jsonify(prediction_result)
        except FileNotFoundError as e:
            return jsonify({"error": str(e)}), 500
        except Exception as e:
            print(f"Prediction error: {str(e)}") # Log the actual error
            return jsonify({"error": f"Prediction failed: {str(e)}"}), 500
        finally:
            os.remove(filepath) # Clean up uploaded file
    return jsonify({"error": "File type not allowed"}), 400

@app.route('/retrain', methods=['POST'])
def retrain():
    if 'data_zip' not in request.files:
        return jsonify({"error": "No data_zip file part"}), 400
    zip_file = request.files['data_zip']
    if zip_file.filename == '':
        return jsonify({"error": "No selected zip file"}), 400
    if zip_file and allowed_file(zip_file.filename):
        filename = secure_filename(zip_file.filename)
        zip_filepath = os.path.join(RETRAIN_DATA_FOLDER, filename)
        zip_file.save(zip_filepath)

        extracted_data_dir = None

        try:
            print(f"Received zip file: {zip_filepath}")
            # Pass DATA_DIR to load_and_preprocess_bulk_data if it needs to know the project root
            extracted_data_dir = load_and_preprocess_bulk_data(zip_filepath, extract_to_dir=os.path.join(PROJECT_ROOT, 'temp_retrain_data'))
            print(f"Data extracted to: {extracted_data_dir}")
            print(f"Contents of extracted data dir: {os.listdir(extracted_data_dir)}")

            train_generator, class_indices = create_data_generator(extracted_data_dir, is_training=True)
            print(f"Train generator found {train_generator.samples} samples belonging to {train_generator.num_classes} classes.")

            if train_generator.samples == 0:
                raise ValueError("The PyDataset has length 0. No images found in the provided zip data.")

            num_classes = len(class_indices)
            model = create_cnn_model(num_classes=num_classes)

            train_model(model, train_generator, epochs=10, model_save_path=MODEL_PATH)

            from src.prediction import _model, _class_names
            _model = None
            _class_names = None

            return jsonify({"message": "Model retraining triggered and completed successfully!", "new_classes": list(class_indices.keys())})
        except Exception as e:
            print(f"Retraining error: {str(e)}")
            return jsonify({"error": f"Retraining failed: {str(e)}"}), 500
        finally:
            os.remove(zip_filepath)
            if extracted_data_dir and os.path.exists(extracted_data_dir):
                shutil.rmtree(extracted_data_dir)

    return jsonify({"error": "Zip file type not allowed"}), 400

# Endpoint to serve static image files from the data directory
@app.route('/data-images/<path:filename>')
def serve_data_image(filename):
    """Serves image files from the DATA_DIR."""
    # Ensure the path is safe and within the DATA_DIR
    return send_from_directory(DATA_DIR, filename)

# Endpoint to provide data insights
@app.route('/data-insights', methods=['GET'])
def get_data_insights():
    insights = {
        "class_distribution": {},
        "sample_images": {},
        "image_dimensions": {
            "min_width": 0, "max_width": 0, "avg_width": 0,
            "min_height": 0, "max_height": 0, "avg_height": 0,
            "total_images": 0
        }
    }

    all_image_paths = []
    train_dir = os.path.join(DATA_DIR, 'train')
    print(f"DEBUG: Resolved train_dir for insights: {train_dir}")

    if not os.path.exists(train_dir):
        return jsonify({"error": "Training data directory not found for insights."}), 404

    # Get class distribution and collect all image paths
    for class_name in os.listdir(train_dir):
        class_path = os.path.join(train_dir, class_name)
        if os.path.isdir(class_path):
            print(f"DEBUG: Checking class path: {class_path}")
            images_in_class = [f for f in os.listdir(class_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            print(f"DEBUG: Found {len(images_in_class)} image files in {class_name}: {images_in_class[:5]}...") # Print first 5
            insights["class_distribution"][class_name] = len(images_in_class)
            
            # Collect sample images (up to 3 per class)
            insights["sample_images"][class_name] = []
            for i, img_name in enumerate(images_in_class):
                if i < 3: # Limit to 3 sample images per class
                    # Return path relative to DATA_DIR for serving
                    relative_path = os.path.join('train', class_name, img_name)
                    insights["sample_images"][class_name].append(relative_path)
                all_image_paths.append(os.path.join(class_path, img_name))

    # Calculate image dimensions
    widths = []
    heights = []
    for img_path in all_image_paths:
        try:
            with Image.open(img_path) as img:
                width, height = img.size
                widths.append(width)
                heights.append(height)
        except Exception as e:
            print(f"ERROR: Could not read image {img_path} for dimensions: {e}")

    if widths and heights:
        insights["image_dimensions"]["min_width"] = min(widths)
        insights["image_dimensions"]["max_width"] = max(widths)
        insights["image_dimensions"]["avg_width"] = float(np.mean(widths))
        insights["image_dimensions"]["min_height"] = min(heights)
        insights["image_dimensions"]["max_height"] = max(heights)
        insights["image_dimensions"]["avg_height"] = float(np.mean(heights))
        insights["image_dimensions"]["total_images"] = len(all_image_paths)

    return jsonify(insights)


if __name__ == '__main__':
    # Ensure a model exists for the API to load initially
    if not os.path.exists(MODEL_PATH):
        print(f"No model found at {MODEL_PATH}. Please run the Jupyter notebook to train and save a model first.")
        print("Creating a dummy model for initial API startup. This model will not be trained.")
        dummy_model = create_cnn_model()
        # Ensure the directory for the model exists before saving
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        dummy_model.save(MODEL_PATH)
        print("Dummy model created.")

    app.run(debug=True, port=5000)
