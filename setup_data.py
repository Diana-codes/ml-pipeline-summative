import kagglehub
import os
import shutil
import PIL
from PIL import Image
from sklearn.model_selection import train_test_split

# Define the dataset to download
DATASET_ID = "shaunthesheep/microsoft-catsvsdogs-dataset"

# Define your project's data directories
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)) # This script's directory
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
TRAIN_DIR = os.path.join(DATA_DIR, 'train')
TEST_DIR = os.path.join(DATA_DIR, 'test')
TRAIN_CATS_DIR = os.path.join(TRAIN_DIR, 'cats')
TRAIN_DOGS_DIR = os.path.join(TRAIN_DIR, 'dogs')
TEST_CATS_DIR = os.path.join(TEST_DIR, 'cats')
TEST_DOGS_DIR = os.path.join(TEST_DIR, 'dogs')

def setup_data_directories():
    """Creates the necessary data directories for the project."""
    os.makedirs(TRAIN_CATS_DIR, exist_ok=True)
    os.makedirs(TRAIN_DOGS_DIR, exist_ok=True)
    os.makedirs(TEST_CATS_DIR, exist_ok=True)
    os.makedirs(TEST_DOGS_DIR, exist_ok=True)
    print("Project data directories created/ensured.")

def is_valid_image(filepath):
    """Checks if an image file is valid and readable, and not zero-byte."""
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        print(f"Skipping missing or zero-byte file: {filepath}")
        return False
    try:
        with Image.open(filepath) as img:
            img.verify() # Verify that it is an image
        return True
    except (IOError, SyntaxError, PIL.UnidentifiedImageError) as e:
        print(f"Skipping corrupted or invalid image: {filepath} ({e})")
        return False

def download_and_organize_kaggle_data():
    """
    Downloads the Kaggle dataset and organizes it into the project's
    train/test/cats/dogs structure.
    """
    print(f"Downloading dataset: {DATASET_ID}...")
    # Download latest version
    kaggle_path = kagglehub.dataset_download(DATASET_ID)
    print(f"Dataset downloaded to: {kaggle_path}")

    # The actual images are inside the 'PetImages' folder
    pet_images_dir = os.path.join(kaggle_path, 'PetImages')

    if not os.path.exists(pet_images_dir):
        print(f"Error: Expected 'PetImages' directory not found at {pet_images_dir}")
        print("Please check the structure of the downloaded Kaggle dataset.")
        # List contents of kaggle_path to help debug if 'PetImages' is not there
        print(f"Contents of {kaggle_path}: {os.listdir(kaggle_path)}")
        return

    cat_source_dir = os.path.join(pet_images_dir, 'Cat')
    dog_source_dir = os.path.join(pet_images_dir, 'Dog')

    if not os.path.exists(cat_source_dir) or not os.path.exists(dog_source_dir):
        print(f"Error: Expected 'Cat' or 'Dog' directories not found within {pet_images_dir}")
        print(f"Contents of {pet_images_dir}: {os.listdir(pet_images_dir)}")
        return

    all_cat_images = [os.path.join(cat_source_dir, f) for f in os.listdir(cat_source_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png')) and is_valid_image(os.path.join(cat_source_dir, f))]
    all_dog_images = [os.path.join(dog_source_dir, f) for f in os.listdir(dog_source_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png')) and is_valid_image(os.path.join(dog_source_dir, f))]

    print(f"Found {len(all_cat_images)} cat images and {len(all_dog_images)} dog images.")

    if not all_cat_images or not all_dog_images:
        print("Warning: One or both image categories are empty. Please check the dataset content.")
        return

    # Split data into training and testing sets
    train_cats, test_cats = train_test_split(all_cat_images, test_size=0.2, random_state=42)
    train_dogs, test_dogs = train_test_split(all_dog_images, test_size=0.2, random_state=42)

    print(f"Splitting into:\n  Cats: {len(train_cats)} train, {len(test_cats)} test\n  Dogs: {len(train_dogs)} train, {len(test_dogs)} test")

    # Copy images to project's train/test directories
    for img_path in train_cats:
        shutil.copy(img_path, os.path.join(TRAIN_CATS_DIR, os.path.basename(img_path)))
    for img_path in train_dogs:
        shutil.copy(img_path, os.path.join(TRAIN_DOGS_DIR, os.path.basename(img_path)))

    for img_path in test_cats:
        shutil.copy(img_path, os.path.join(TEST_CATS_DIR, os.path.basename(img_path)))
    for img_path in test_dogs:
        shutil.copy(img_path, os.path.join(TEST_DOGS_DIR, os.path.basename(img_path)))

    print("Images successfully organized into project's data directories.")

# This block ensures the functions are called when the script is executed directly
if __name__ == "__main__":
    setup_data_directories()
    download_and_organize_kaggle_data()