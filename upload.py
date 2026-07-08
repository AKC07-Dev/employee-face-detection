import boto3
import json

bucket = "employee-photo-demo-antara"
image = "employee.jpg"

s3 = boto3.client("s3")

rekognition = boto3.client("rekognition")

print("Uploading image...")

s3.upload_file(image, bucket, image)

print("Upload Successful")

response = rekognition.detect_faces(

    Image={
        "S3Object": {
            "Bucket": bucket,
            "Name": image
        }
    },

    Attributes=["ALL"]

)

faces = response["FaceDetails"]

print("Faces Detected:", len(faces))

result = []

for i, face in enumerate(faces):

    confidence = face["Confidence"]

    print(f"Face {i+1}: {confidence:.2f}%")

    result.append({

        "face": i + 1,

        "confidence": confidence

    })

with open("result.json", "w") as f:

    json.dump(result, f, indent=4)

print("result.json created")
