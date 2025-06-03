import tensorflow as tf
import numpy as np
from PIL import Image
import io

# Load the model once (adjust path as needed)
model = tf.keras.models.load_model('../backend/model.h5')

# Load class names from file
with open('../backend/class_names.txt', 'r') as f:
    class_names = [line.strip() for line in f.readlines()]

# Mapping from folder/class names to user-friendly labels
label_map = {
    "Pepper__bell___Bacterial_spot": "Pepper Bacterial Spot",
    "Pepper__bell___healthy": "Healthy Pepper",
    "PlantVillage": "Unknown / Miscellaneous",
    "Potato___Early_blight": "Potato Early Blight",
    "Potato___Late_blight": "Potato Late Blight",
    "Potato___healthy": "Healthy Potato",
    "Tomato_Bacterial_spot": "Tomato Bacterial Spot",
    "Tomato_Early_blight": "Tomato Early Blight",
    "Tomato_Late_blight": "Tomato Late Blight",
    "Tomato_Leaf_Mold": "Tomato Leaf Mold",
    "Tomato_Septoria_leaf_spot": "Tomato Septoria Leaf Spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite": "Tomato Spider Mites",
    "Tomato__Target_Spot": "Tomato Target Spot",
    "Tomato__Tomato_YellowLeaf__Curl_Virus": "Tomato Yellow Leaf Curl Virus",
    "Tomato__Tomato_mosaic_virus": "Tomato Mosaic Virus",
    "Tomato_healthy": "Healthy Tomato"
}

IMAGE_SIZE = (224, 224)

def preprocess_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    img = img.resize(IMAGE_SIZE)
    img_array = np.array(img) / 255.0  # normalize
    return np.expand_dims(img_array, axis=0)

def predict(image_bytes):
    img = preprocess_image(image_bytes)
    preds = model.predict(img)
    pred_index = np.argmax(preds)
    confidence = preds[0][pred_index]

    class_folder_name = class_names[pred_index]
    friendly_label = label_map.get(class_folder_name, class_folder_name)

    return {
        "pest": friendly_label,
        "confidence": float(confidence)
    }
