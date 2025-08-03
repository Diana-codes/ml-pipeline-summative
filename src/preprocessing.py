import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import os
import zipfile

IMG_HEIGHT = 128
IMG_WIDTH = 128

def preprocess_single_image(image_path):
    """
    Loads and preprocesses a single image for prediction.
    """
    img = image.load_img(image_path, target_size=(IMG_HEIGHT, IMG_WIDTH))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) # Create a batch dimension
    img_array /= 255.0 # Normalize to [0, 1]
    return img_array

def load_and_preprocess_bulk_data(zip_file_path, extract_to_dir='temp_retrain_data'):
    """
    Extracts a zip file containing new training data and prepares it for retraining.
    Assumes the zip file contains class subdirectories (e.g., 'data.zip' -> 'data/class_a', 'data/class_b').
    Returns the path to the extracted data directory.
    """
    if os.path.exists(extract_to_dir):
        import shutil
        shutil.rmtree(extract_to_dir) # Clean up previous extraction
    os.makedirs(extract_to_dir, exist_ok=True)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to_dir)
    print(f"Extracted data to: {extract_to_dir}")

    # Verify structure (optional, but good for debugging)
    extracted_content = os.listdir(extract_to_dir)
    print(f"Content of extracted directory: {extracted_content}")
    if len(extracted_content) == 1 and os.path.isdir(os.path.join(extract_to_dir, extracted_content[0])):
        # If zip contains a single root folder, use that as the data directory
        return os.path.join(extract_to_dir, extracted_content[0])
    return extract_to_dir

def create_data_generator(data_dir, batch_size=32, shuffle=True, is_training=True):
    """
    Creates an ImageDataGenerator for training or evaluation.
    """
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    if is_training:
        datagen = image.ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )
    else:
        datagen = image.ImageDataGenerator(rescale=1./255)

    # Determine class_mode based on number of subdirectories (classes)
    num_classes = len([d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))])
    class_mode = 'categorical' if num_classes > 2 else 'binary'

    generator = datagen.flow_from_directory(
        data_dir,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=batch_size,
        class_mode=class_mode,
        shuffle=shuffle
    )
    return generator, generator.class_indices
