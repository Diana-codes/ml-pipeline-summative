import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
import os

IMG_HEIGHT = 128
IMG_WIDTH = 128
NUM_CLASSES = 2 # Default, will be updated based on data in retraining

def create_cnn_model(input_shape=(IMG_HEIGHT, IMG_WIDTH, 3), num_classes=NUM_CLASSES):
    """
    Defines and compiles a simple Convolutional Neural Network (CNN) model.
    """
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax' if num_classes > 2 else 'sigmoid')
    ])

    model.compile(optimizer='adam',
                  loss='categorical_crossentropy' if num_classes > 2 else 'binary_crossentropy',
                  metrics=['accuracy'])
    return model

def train_model(model, train_generator, epochs=10, model_save_path='../models/image_classifier_model.tf'):
    """
    Trains the given model using the provided data generator and saves it.
    """
    print(f"Starting training for {epochs} epochs...")
    history = model.fit(
        train_generator,
        epochs=epochs
    )
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    model.save(model_save_path)
    print(f"Model saved to: {model_save_path}")
    return history
