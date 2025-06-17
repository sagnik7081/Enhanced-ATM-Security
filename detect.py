import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
from scipy.spatial.distance import cosine
import alerts
import os
import threading
import time
import requests
import json


API_URL = "http://localhost:5000/api"


AUTHORIZED_DIR = "authorized_faces"
BANNED_DIR = "banned_faces"
UNAUTHORIZED_DIR = "unauthorized_faces"

for folder in [AUTHORIZED_DIR, BANNED_DIR, UNAUTHORIZED_DIR]:
    os.makedirs(folder, exist_ok=True)


approved_persons = set()
banned_persons = set()


app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=0, det_size=(640, 640))


try:
    data = np.load("embeddings.npz", allow_pickle=True)
    stored_embeddings = data["embeddings"]
    stored_labels = data["labels"]
except:
    print("[WARNING] No embeddings.npz found, using empty embeddings")
    stored_embeddings = []
    stored_labels = []


def extract_embedding(frame):
    faces = app.get(frame)
    if len(faces) == 0:
        return None, None
    return faces[0].embedding, faces[0].bbox


def verify_face(embedding):
    if len(stored_embeddings) == 0:
        return "Unauthorized"
        
    min_distance = float("inf")
    best_match = None

    for stored_embedding, label in zip(stored_embeddings, stored_labels):
        distance = cosine(embedding, stored_embedding)
        if distance < min_distance:
            min_distance = distance
            best_match = label

    return best_match if min_distance < 0.5 else "Unauthorized"


def save_face_image(frame, face_id, bbox, folder):
    x1, y1, x2, y2 = map(int, bbox)
    face_img = frame[y1:y2, x1:x2]
    file_path = os.path.join(folder, f"{face_id}.jpg")
    cv2.imwrite(file_path, face_img)
    print(f"[INFO] Saved face image: {file_path}")


def register_alert_with_api(face_id):
    try:
        response = requests.post(
            f"{API_URL}/alerts/new",
            json={"face_id": face_id},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print(f"[INFO] Alert registered with API for {face_id}")
            return True
        else:
            print(f"[ERROR] Failed to register alert: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] API connection error: {e}")
        return False


def check_status_from_api(face_id):
    try:
        response = requests.get(f"{API_URL}/status/{face_id}")
        if response.status_code == 200:
            data = response.json()
            return data.get("status")
        else:
            print(f"[ERROR] Failed to get status: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] API connection error: {e}")
        return None

def wait_for_approval(face_id, embedding, frame, bbox):
    print(f"[INFO] Waiting for approval for {face_id}")

    # Always register with API
    register_alert_with_api(face_id)

    # Try to send email with full error details
    try:
        alerts.send_email(face_id, "sagnik94552@gmail.com")
        print("[INFO] Email function called successfully!")
    except Exception as e:
        print(f"[ERROR] Email sending failed: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full stack trace

    # Try to send SMS with full error details
    try:
        alerts.send_sms(face_id, "+917081239249")
        print("[INFO] SMS function called successfully!")
    except Exception as e:
        print(f"[ERROR] SMS sending failed: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full stack trace


def poll_status(face_id, embedding, frame, bbox):
    while True:
        status = check_status_from_api(face_id)
        
        
        if status is None:
            status = alerts.get_status(face_id)
        
        if status == "approved":
            approved_persons.add(tuple(embedding))
            save_face_image(frame, face_id, bbox, AUTHORIZED_DIR)
            print(f"[INFO] {face_id} approved. Saved in authorized_faces.")
            return
            
        elif status == "banned":
            banned_persons.add(tuple(embedding))
            save_face_image(frame, face_id, bbox, BANNED_DIR)
            print(f"[ALERT] {face_id} banned! System shutting down.")
            os._exit(0)  
            
        time.sleep(2)  

def start_detection():
    
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Face Verification", cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to capture frame")
            break

        embedding, bbox = extract_embedding(frame)

        if embedding is not None:
            if tuple(embedding) in approved_persons:
                cv2.putText(frame, "Approved", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            elif tuple(embedding) in banned_persons:
                cv2.putText(frame, "BANNED", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                print("[ALERT] Banned user detected! System shutting down.")
                break
            
            else:
                identity = verify_face(embedding)

                if identity == "Unauthorized":
                    face_id = f"unknown_{int(time.time())}"
                    
                    if bbox is not None:
                        save_face_image(frame, face_id, bbox, UNAUTHORIZED_DIR)
                    
                    
                    approval_thread = threading.Thread(
                        target=wait_for_approval, 
                        args=(face_id, embedding, frame, bbox)
                    )
                    approval_thread.daemon = True
                    approval_thread.start()
                    
                    cv2.putText(frame, "Unauthorized! Alert Sent", (30, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                else:
                    cv2.putText(frame, f"Identity: {identity}", (30, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


        cv2.imshow("Face Verification", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_detection()