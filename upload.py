import boto3
import json
import glob
import os

# ----------------------------
# AWS Configuration
# ----------------------------
bucket = "employee-photo-demo-antara"

# ----------------------------
# Find image automatically
# ----------------------------
images = (
    glob.glob("*.jpg") +
    glob.glob("*.jpeg") +
    glob.glob("*.png") +
    glob.glob("*.JPG") +
    glob.glob("*.JPEG") +
    glob.glob("*.PNG")
)

if not images:
    raise Exception("No image (.jpg/.jpeg/.png) found in the repository.")

image = images[0]

print(f"Using image: {image}")

# ----------------------------
# Create AWS clients
# ----------------------------
s3 = boto3.client("s3")
rekognition = boto3.client("rekognition")

# ----------------------------
# Upload image to S3
# ----------------------------
print("Uploading image to S3...")

s3.upload_file(image, bucket, os.path.basename(image))

print("Upload Successful!")

# ----------------------------
# Detect faces
# ----------------------------
print("Running Amazon Rekognition...")

response = rekognition.detect_faces(
    Image={
        "S3Object": {
            "Bucket": bucket,
            "Name": os.path.basename(image)
        }
    },
    Attributes=["ALL"]
)

faces = response["FaceDetails"]

print("\n========== RESULT ==========")
print(f"Image: {image}")
print(f"Number of Faces: {len(faces)}")

result = {
    "image": image,
    "number_of_faces": len(faces),
    "faces": []
}

for i, face in enumerate(faces, start=1):
    confidence = round(face["Confidence"], 2)

    print(f"Face {i} Confidence: {confidence}%")

    result["faces"].append({
        "face_number": i,
        "confidence": confidence
    })

# ----------------------------
# Save JSON
# ----------------------------
with open("result.json", "w") as f:
    json.dump(result, f, indent=4)

print("\nresult.json created successfully!")
