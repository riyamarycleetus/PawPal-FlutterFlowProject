from flask import Flask, request, jsonify
import boto3
import base64

app = Flask(__name__)
app.static_folder = 'static'  # Configure Flask to serve static files from the 'static' directory

# AWS credentials and region
AWS_REGION = 'us-east-1'
AWS_CUSTOM_MODEL_ARN = 'arn:aws:rekognition:us-east-1:058264217533:project/BreedIdentifier/version/BreedIdentifier.2024-04-27T11.45.12/1714198515365'

# Initialize Boto3 client without credentials
rekognition = boto3.client('rekognition', region_name=AWS_REGION)

@app.route('/', methods=['GET', 'POST'])
def detect_breeds():
    if request.method == 'POST':
        try:
            # Get the uploaded image
            image = request.files['image']
            
            # Perform Breed detection using the custom model
            response = rekognition.detect_custom_labels(
                Image={'Bytes': image.read()},
                MinConfidence=60,
                ProjectVersionArn=AWS_CUSTOM_MODEL_ARN
            )
            
            # Extract labels from the response
            labels = [label['Name'] for label in response['CustomLabels']]
            
            # Rewind the file pointer to read the image data again
            image.seek(0)
            image_data = base64.b64encode(image.read()).decode('utf-8')
            
            return jsonify({'labels': labels, 'image_data': image_data})
        except Exception as e:
            return jsonify({'error': str(e)})
    
    # HTML front-end code (unchanged)
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Breed Identifier</title>
    <link href="https://fonts.googleapis.com/css2?family=Teko&display=swap" rel="stylesheet">
    <style>
        body {
            background-image: url('/static/bg2.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            color: white;
            font-family: 'Teko', sans-serif;
            text-align: center;
            padding: 20px;
            margin: 0;
        }
        h1 {
            font-size: 40px;
            margin-bottom: 30px;
        }
        .content {
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100vh;
            justify-content: center;
        }
        #uploadedImage {
            max-width: 90vw;
            max-height: 50vh;
            margin-bottom: 20px;
        }
        /* Style for buttons */
        .button {
            padding: 2vw 4vw;
            font-size: 3vw;
            background-color: rgba(245, 245, 220, 0.6); /* Transparent white */
            border: none;
            color: white;
            text-align: center;
            text-decoration: none;
            margin: 2vw;
            cursor: pointer;
            border-radius: 8px;
            transition-duration: 0.4s;
            font-weight: bold;
        }
        .button:hover {
            background-color: rgba(255, 255, 255, 0.5); /* Darker transparent white */
        }
        #fileInput {
            padding: 2vw 4vw;
            font-size: 3vw;
            background-color: rgba(255, 255, 255, 0.3); /* Transparent white */
            border: none;
            color: white;
            text-align: center;
            text-decoration: none;
            margin: 2vw;
            cursor: pointer;
            border-radius: 8px;
            transition-duration: 0.4s;
        }
        /* Container for result labels */
        #resultContainer {
            background-color: rgba(0, 0, 0, 0.5); /* Semi-transparent black */
            border-radius: 8px;
            margin-top: 2vw;
            padding: 4vw;
        }
        /* Style for result labels */
        .resultLabel {
            color: white;
            font-size: 20px;
            text-transform: uppercase; 
        }
    </style>
</head>
<body>
    <div class="content">
        <h1>Breed Identifier</h1>
        <form id="uploadForm" enctype="multipart/form-data">
            <input type="file" id="fileInput" accept="image/*" onchange="previewImage(event)">
            <button type="button" class="button" onclick="detectBreeds()">Detect Breeds</button>
        </form>
        <img id="uploadedImage" src="#" alt="Uploaded Image">
        <!-- Container for result labels -->
        <div id="resultContainer"></div>
    </div>
    <script>
        function previewImage(event) {
            const file = event.target.files[0];
            const reader = new FileReader();
            reader.onload = function() {
                const imgElement = document.getElementById('uploadedImage');
                imgElement.src = reader.result;
                imgElement.style.display = 'block'; // Show the image
            };
            reader.readAsDataURL(file);
        }

        async function detectBreeds() {
            const formData = new FormData();
            formData.append('image', document.getElementById('fileInput').files[0]);
            const response = await fetch('/', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            const resultContainer = document.getElementById('resultContainer');
            resultContainer.innerHTML = ''; // Clear previous results
            if ('error' in data) {
                resultContainer.textContent = data.error;
            } else {
                data.labels.forEach((label) => {
                    const p = document.createElement('p');
                    p.textContent = label;
                    p.classList.add('resultLabel'); // Add a class for styling
                    resultContainer.appendChild(p);
                });
            }
        }
    </script>
</body>
</html>

    """

if __name__ == '__main__':
    app.run(debug=True)
