import boto3
import json
import glob
import os
import sys

# -----------------------------
# AWS Configuration
# -----------------------------
bucket = "employee-photo-demo-antara"

# AWS Clients
s3 = boto3.client("s3")
rekognition = boto3.client("rekognition")

# -----------------------------
# Find newest image
# -----------------------------
extensions = [
    "*.jpg",
    "*.jpeg",
    "*.png",
    "*.webp"
]

files = []

for ext in extensions:
    files.extend(glob.glob(f"images/{ext}"))

if len(files) == 0:
    print("No images found inside images folder.")
    sys.exit(1)

latest = max(files, key=os.path.getctime)

original_filename = os.path.basename(latest)

print(f"Image Selected: {original_filename}")

# -----------------------------
# Upload image to S3
# -----------------------------
print("Uploading image to S3...")

s3.upload_file(
    latest,
    bucket,
    "latest.jpg"
)

print("Upload Successful!")

# -----------------------------
# Detect Faces
# -----------------------------
response = rekognition.detect_faces(

    Image={
        "S3Object": {
            "Bucket": bucket,
            "Name": "latest.jpg"
        }
    },

    Attributes=["ALL"]

)

faces = response["FaceDetails"]

print("-----------------------------------")
print(f"Image: {original_filename}")
print(f"Number of Faces: {len(faces)}")
print("-----------------------------------")

face_data = []

for i, face in enumerate(faces):

    confidence = round(face["Confidence"], 2)

    print(f"Face {i+1} Confidence: {confidence}%")

    face_data.append({
        "face_number": i + 1,
        "confidence": confidence
    })

# -----------------------------
# Create JSON
# -----------------------------
result = {

    "image": original_filename,

    "number_of_faces": len(faces),

    "faces": face_data

}

with open("result.json", "w") as f:
    json.dump(result, f, indent=4)

print("\nresult.json created successfully!")

# -----------------------------
# Upload result.json to S3
# -----------------------------
s3.upload_file(
    "result.json",
    bucket,
    "result.json"
)

print("result.json uploaded to S3!")

print("\nWebsite Updated Successfully!")
