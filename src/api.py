from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1' # Force TensorFlow to use CPU
import shutil
import tempfile
from flask_cors import CORS # Import CORS

# Import functions from our src modules
from src.preprocessing import preprocess_single_image, load_and_preprocess_bulk_data, create_data_generator
from src.model import create_cnn_model, train_model
from src.prediction import load_ml_model, predict_image

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
RETRAIN_DATA_FOLDER = 'retrain_data'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'zip'}
MODEL_PATH = '../models/image_classifier_model.tf'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RETRAIN_DATA_FOLDER, exist_ok=True)

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

        try:
            # Load and preprocess new data
            extracted_data_dir = load_and_preprocess_bulk_data(zip_filepath)
            train_generator, class_indices = create_data_generator(extracted_data_dir, is_training=True)

            # Re-create model (or load and continue training)
            # For simplicity, we'll create a new model. For continuous learning,
            # you might load the existing model and continue training.
            num_classes = len(class_indices)
            model = create_cnn_model(num_classes=num_classes)

            # Train the model with new data
            train_model(model, train_generator, epochs=10, model_save_path=MODEL_PATH)

            # Invalidate loaded model in prediction.py to force reload
            from src.prediction import _model, _class_names
            _model = None
            _class_names = None

            return jsonify({"message": "Model retraining triggered and completed successfully!", "new_classes": list(class_indices.keys())})
        except Exception as e:
            return jsonify({"error": f"Retraining failed: {str(e)}"}), 500
        finally:
            os.remove(zip_filepath) # Clean up uploaded zip
            # Clean up extracted data
            if 'extracted_data_dir' in locals() and os.path.exists(extracted_data_dir):
                shutil.rmtree(extracted_data_dir)

    return jsonify({"error": "Zip file type not allowed"}), 400

if __name__ == '__main__':
    # Ensure a model exists for the API to load initially
    if not os.path.exists(MODEL_PATH):
        print(f"No model found at {MODEL_PATH}. Please run the Jupyter notebook to train and save a model first.")
        print("Creating a dummy model for initial API startup. This model will not be trained.")
        dummy_model = create_cnn_model()
        MODEL_PATH = "../models/image_classifier_model.h5"
        print("Dummy model created.")

    app.run(debug=True, port=5000)
