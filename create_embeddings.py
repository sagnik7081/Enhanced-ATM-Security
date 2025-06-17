import os
import numpy as np
import cv2
from tqdm import tqdm
import insightface
from insightface.app import FaceAnalysis

# ✅ Initialize ArcFace model with detection threshold
app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=0, det_size=(640, 640))  # Increased size for better detection

# ✅ Use the correct dataset folder!
dataset_path = "processed_dataset/authorized"
embedding_file = "embeddings.npz"

# Initialize storage
embeddings = []
labels = []

# Define function to extract ArcFace embeddings
def extract_embedding(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"[ERROR] Cannot read image: {image_path}")
        return None

    # ✅ Debug: Show an image if needed
    # cv2.imshow("Test Image", img)
    # cv2.waitKey(0)
    
    faces = app.get(img)  # Detect faces

    if len(faces) == 0:
        print(f"[WARNING] No face detected in: {image_path}")

        # ✅ Debug: Save failed images to check manually
        debug_path = "debug_failed_faces"
        os.makedirs(debug_path, exist_ok=True)
        cv2.imwrite(os.path.join(debug_path, os.path.basename(image_path)), img)
        
        return None

    return faces[0].embedding  # Extract 512D embedding

# Loop through each person
for person in os.listdir(dataset_path):
    person_path = os.path.join(dataset_path, person)
    
    if not os.path.isdir(person_path):
        continue  # Skip non-folder files
    
    image_files = [os.path.join(person_path, f) for f in os.listdir(person_path) if f.endswith((".jpg", ".png"))]
    
    print(f"\n[DEBUG] Processing {person} - Found {len(image_files)} images")  # Debug print
    
    for image_path in tqdm(image_files):
        embedding = extract_embedding(image_path)
        
        if embedding is not None:
            embeddings.append(embedding)
            labels.append(person)
        else:
            print(f"[ERROR] Failed to extract embedding for {image_path}")

# Save embeddings
if len(embeddings) > 0:
    np.savez(embedding_file, labels=labels, embeddings=np.array(embeddings))
    print("[INFO] Embeddings saved successfully.")
else:
    print("[ERROR] No embeddings were extracted!")
