import boto3
import json
import glob
import os

# ===========================
# AWS Clients
# ===========================
s3 = boto3.client("s3")
rekognition = boto3.client("rekognition")

# ===========================
# Bucket Name
# ===========================
bucket = "employee-photo-demo-antara"

# ===========================
# Find any image automatically
# ===========================
extensions = ["*.jpg", "*.jpeg", "*.png"]

images = []

for ext in extensions:
    images.extend(glob.glob(ext))

if not images:
    raise Exception("No image found in repository!")

image = images[0]

print(f"\nUploading image: {image}")

# ===========================
# Upload Image
# ===========================
s3.upload_file(image, bucket, image)

print("Upload Successful")

# ===========================
# Rekognition
# ===========================
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

print("\n============================")
print(f"Image: {image}")
print(f"Number of Faces: {len(faces)}")

result = []

for i, face in enumerate(faces):

    confidence = round(face["Confidence"], 2)

    print(f"Face {i+1} Confidence: {confidence}%")

    result.append({
        "face": i + 1,
        "confidence": confidence
    })

# ===========================
# Save JSON
# ===========================
output = {
    "image": image,
    "number_of_faces": len(faces),
    "faces": result
}

with open("result.json", "w") as f:
    json.dump(output, f, indent=4)

print("\nresult.json created successfully!")

# ===========================
# Create HTML
# ===========================
html = f"""
<!DOCTYPE html>
<html>

<head>

<title>Employee Face Detection</title>

<style>

body{{
font-family:Arial;
background:#f5f5f5;
padding:40px;
}}

.container{{
background:white;
padding:30px;
border-radius:10px;
width:700px;
margin:auto;
box-shadow:0 0 15px rgba(0,0,0,.2);
}}

img{{
width:350px;
margin:20px 0;
border-radius:10px;
}}

h1{{
color:#0b5394;
}}

pre{{
background:#efefef;
padding:15px;
border-radius:8px;
}}

</style>

</head>

<body>

<div class="container">

<h1>Employee Face Detection Report</h1>

<h3>Latest Uploaded Image</h3>

<img src="{image}">

<h3>Detection Logs</h3>

<pre>
Image: {image}

Number of Faces: {len(faces)}
"""

for i, face in enumerate(result):
    html += f"Face {i+1} Confidence: {face['confidence']}%\n"

html += """

result.json created successfully!

</pre>

</div>

</body>

</html>
"""

with open("index.html", "w") as f:
    f.write(html)

print("index.html created!")

# ===========================
# Upload Outputs
# ===========================
s3.upload_file(
    "index.html",
    bucket,
    "index.html",
    ExtraArgs={"ContentType": "text/html"}
)

s3.upload_file(
    "result.json",
    bucket,
    "result.json",
    ExtraArgs={"ContentType": "application/json"}
)

print("index.html uploaded to S3")
print("result.json uploaded to S3")

print("\nAutomation Completed Successfully!")
