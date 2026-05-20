# =========================================================
# AI ENGINE
# =========================================================

import cv2
import easyocr
import numpy as np

from PIL import Image



# =========================================================
# LOAD OCR
# =========================================================

reader = easyocr.Reader(

    ['en'],

    gpu=False

)

# =========================================================
# LOAD AI MODEL
# =========================================================

base_model = MobileNetV2(

    weights="imagenet",

    include_top=False,

    pooling="avg"

)

model = Model(

    inputs=base_model.input,

    outputs=base_model.output

)

# =========================================================
# OCR TEXT EXTRACTION
# =========================================================

def extract_text(image_path):

    try:

        results = reader.readtext(

            image_path,

            detail=0

        )

        text = " ".join(results)

        return text

    except Exception as e:

        print("OCR ERROR:", e)

        return ""

# =========================================================
# IMAGE EMBEDDING
# =========================================================

def generate_embedding(image_path):

    try:

        image = Image.open(
            image_path
        )

        image = image.convert("RGB")

        image = image.resize(
            (224, 224)
        )

        image_array = img_to_array(
            image
        )

        image_array = np.expand_dims(
            image_array,
            axis=0
        )

        image_array = preprocess_input(
            image_array
        )

        embedding = model.predict(
            image_array
        )

        return embedding.flatten()

    except Exception as e:

        print("EMBEDDING ERROR:", e)

        return None

# =========================================================
# COSINE SIMILARITY
# =========================================================

def cosine_similarity(vec1, vec2):

    dot_product = np.dot(vec1, vec2)

    norm1 = np.linalg.norm(vec1)

    norm2 = np.linalg.norm(vec2)

    return dot_product / (
        norm1 * norm2
    )

# =========================================================
# MATCH IMAGES
# =========================================================

def compare_images(

    image1,

    image2

):

    emb1 = generate_embedding(
        image1
    )

    emb2 = generate_embedding(
        image2
    )

    if emb1 is None or emb2 is None:

        return 0

    similarity = cosine_similarity(

        emb1,
        emb2

    )

    return similarity