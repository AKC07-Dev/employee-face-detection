import boto3
import json
import glob

bucket = "employee-photo-demo-antara"

# -----------------------------
# Find first image automatically
# -----------------------------
images = []

for ext in ("*.jpg", "*.jpeg", "*.png"):
    images.extend(glob.glob(ext))

if not images:
    raise Exception("No image found!")

image = images[0]

print(f"Uploading {image}...")

s3 = boto3.client("s3")
rekognition = boto3.client("rekognition")

# Upload image
s3.upload_file(image, bucket, image)

print("Upload Successful")

# Detect Faces
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

print()
print("Image:", image)
print("Number of Faces:", len(faces))

results = []

for i, face in enumerate(faces):

    confidence = round(face["Confidence"], 2)

    print(f"Face {i+1} Confidence: {confidence}%")

    results.append({

        "face": i + 1,

        "confidence": confidence

    })

# Save result.json

output = {

    "image": image,

    "number_of_faces": len(faces),

    "faces": results

}

with open("result.json", "w") as f:
    json.dump(output, f, indent=4)

print()
print("result.json created successfully!")

# -----------------------------
# Create HTML Automatically
# -----------------------------

html = f"""

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>Employee Face Detection</title>

<style>

body{{
font-family:Arial;
background:#f4f4f4;
padding:40px;
}}

.container{{
max-width:700px;
margin:auto;
background:white;
padding:30px;
border-radius:10px;
box-shadow:0 0 10px gray;
}}

img{{
width:300px;
border-radius:10px;
margin-bottom:20px;
}}

h1{{
color:#0066cc;
}}

</style>

</head>

<body>

<div class="container">

<h1>Employee Face Detection Report</h1>

<img src="{image}" width="300">

<h3>Image:</h3>

<p>{image}</p>

<h3>Number of Faces:</h3>

<p>{len(faces)}</p>

<h3>Confidence:</h3>

"""

for face in results:

    html += f"<p>Face {face['face']} Confidence : {face['confidence']}%</p>"

html += """

</div>

</body>

</html>

"""

with open("index.html", "w") as f:
    f.write(html)

print("index.html created!")

# Upload Files

s3.upload_file(
    "result.json",
    bucket,
    "result.json",
    ExtraArgs={"ContentType":"application/json"}
)

s3.upload_file(
    "index.html",
    bucket,
    "index.html",
    ExtraArgs={"ContentType":"text/html"}
)

print("index.html uploaded")
print("result.json uploaded")

print()
print("Automation Completed Successfully!")
