import os
import cv2
import numpy as np
from tqdm import tqdm

# Define dataset paths
authorized_path = "dataset/authorized"
unauthorized_path = "dataset/unauthorized"
preprocessed_path = "processed_dataset"  # ✅ Corrected folder name

os.makedirs(preprocessed_path, exist_ok=True)

# Function to preprocess images
def preprocess_image(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"[WARNING] Cannot read: {image_path}")
            return None
        img = cv2.resize(img, (250, 250))  # Resize to 250x250
        img = img.astype("float32") / 255.0  # Normalize
        return img
    except Exception as e:
        print(f"[ERROR] Failed to process {image_path}: {e}")
        return None

# Function to process dataset while maintaining correct structure
def process_dataset(dataset_path, dataset_type):
    image_files = []
    
    # Collect all image paths
    for root, _, files in os.walk(dataset_path):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp")):
                image_files.append(os.path.join(root, file))

    total_images = len(image_files)
    print(f"Processing {dataset_path}... Total images: {total_images}")

    processed_count = 0
    for image_path in tqdm(image_files, total=total_images, desc=f"Processing {dataset_type} images"):
        if dataset_type == "authorized":
            person_name = os.path.basename(os.path.dirname(image_path))  # Keep folder structure
            save_dir = os.path.join(preprocessed_path, dataset_type, person_name)  
        else:
            save_dir = os.path.join(preprocessed_path, dataset_type)  # ✅ No extra subfolder
        
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, os.path.basename(image_path))
        processed_img = preprocess_image(image_path)

        if processed_img is not None:
            cv2.imwrite(save_path, (processed_img * 255).astype(np.uint8))
            processed_count += 1

    print(f"[INFO] Preprocessing Complete for {dataset_path}! Processed {processed_count}/{total_images} images.")

# Process authorized dataset
if os.path.exists(authorized_path):
    process_dataset(authorized_path, "authorized")
else:
    print(f"[WARNING] {authorized_path} does not exist!")

# Process unauthorized dataset
if os.path.exists(unauthorized_path):
    process_dataset(unauthorized_path, "unauthorized")
else:
    print(f"[WARNING] {unauthorized_path} does not exist!")
