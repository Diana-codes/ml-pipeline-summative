import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
import os

MODEL_PATH = 'models/image_classifier_model.h5'
# This will be dynamically set when the model is loaded or retrained
CLASS_NAMES = ['cats', 'dogs']

_model = None # Global variable to store the loaded model
_class_names = None # Global variable to store class names

def load_ml_model(model_path=MODEL_PATH):
    """
    Loads the pre-trained machine learning model.
    Uses a singleton pattern to load the model only once.
    """
    global _model, _class_names
    if _model is None:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}. Please train the model first.")
        _model = load_model(model_path)
        print(f"Model loaded successfully from {model_path}")

        # Attempt to infer class names from the training data if available
        # In a real application, class names would be saved alongside the model
        # or passed explicitly. For this example, we'll assume a default or try to infer.
        try:
            # This is a simplified way to get class names.
            # In a robust system, you'd save class_indices from ImageDataGenerator.
            from src.preprocessing import create_data_generator
            temp_data_dir = '../data/train' # Assuming original training data is here
            if os.path.exists(temp_data_dir):
                _, class_indices = create_data_generator(temp_data_dir, shuffle=False, is_training=False)
                _class_names = sorted(class_indices, key=class_indices.get)
                print(f"Inferred class names: {_class_names}")
            else:
                _class_names = CLASS_NAMES # Fallback to default
        except Exception as e:
            print(f"Could not infer class names from data directory: {e}. Using default.")
            _class_names = CLASS_NAMES
    return _model, _class_names

def predict_image(preprocessed_image_array):
    """
    Makes a prediction on a preprocessed image array.
    """
    model, class_names = load_ml_model()
    predictions = model.predict(preprocessed_image_array)

    if len(class_names) > 2: # Multi-class classification
        predicted_class_index = np.argmax(predictions, axis=1)[0]
        confidence = np.max(predictions)
    else: # Binary classification
        predicted_class_index = (predictions > 0.5).astype(int)[0][0]
        confidence = predictions[0][0] if predicted_class_index == 1 else (1 - predictions[0][0])

    predicted_class_name = class_names[predicted_class_index]

    return {
        "predicted_class": predicted_class_name,
        "confidence": float(confidence),
        "raw_predictions": predictions.tolist()
    }