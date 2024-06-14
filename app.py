import streamlit as st
import os
import subprocess
from pathlib import Path
import glob
from PIL import Image

# Function to run the test_addsr.py script
def run_test_addsr(image_name):
    try:
        pretrained_model_path = "preset/models/stable-diffusion-2-base"
        addsr_model_path = "preset/addsr"
        ram_ft_path = "preset/models/DAPE.pth"
        image_path = f"preset/datasets/test_datasets/{image_name}"
        output_dir = "preset/datasets/output"
        start_point = "lr"
        num_inference_steps = 4
        PSR_weight = 0.5
        
        command = [
            "python", "test_addsr.py",
            "--pretrained_model_path", pretrained_model_path,
            "--prompt", '',
            "--addsr_model_path", addsr_model_path,
            "--ram_ft_path", ram_ft_path,
            "--image_path", image_path,
            "--output_dir", output_dir,
            "--start_point", start_point,
            "--num_inference_steps", str(num_inference_steps),
            "--PSR_weight", str(PSR_weight)
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            st.error(f"Error: {result.stderr}")
        return result
    except Exception as e:
        st.error(f"An error occurred while running the test_addsr script: {e}")
        return None

# Function to get the latest modified file in a directory
def get_latest_file(directory):
    try:
        files = glob.glob(f"{directory}/*")
        latest_file = max(files, key=os.path.getctime)
        return latest_file
    except Exception as e:
        st.error(f"An error occurred while fetching the latest file: {e}")
        return None

# Function to get file size in KB
def get_file_size(file_path):
    try:
        # Get file size in bytes
        file_size_bytes = os.path.getsize(file_path)
        # Convert to KB
        file_size_kb = file_size_bytes / 1024
        return file_size_kb
    except Exception as e:
        st.error(f"An error occurred while getting file size: {e}")
        return None

# Initialize chat history list
chat_history = []

st.title('Make Your Low Resolution Image in High Resolution') # Image Super-Resolution using AddSR

# Image upload
uploaded_file = st.file_uploader("Choose an image of size less than 5.5 kb...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    try:
        # Save the uploaded file to the test dataset directory
        image_name = uploaded_file.name
        image_path = f"preset/datasets/test_datasets/{image_name}"
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File {image_name} uploaded successfully")
        
        # Add upload message to chat history
        chat_history.append(("User", f"uploaded image: {image_name}", image_path))

        # Display the uploaded image and the output image side by side
        cols = st.columns(2)
        with cols[0]:
            st.image(image_path, caption='Your Image', use_column_width=True) # Uploaded Image

        # Run the test_addsr script
        with st.spinner("Let's enhance the image quality..."): # Running super-resolution...
            result = run_test_addsr(image_name)

        # Display the output image and its size in KB
        latest_file = get_latest_file("preset/datasets/output/sample00")
        if latest_file:
            with cols[1]:
                output_image = Image.open(latest_file)
                st.image(output_image, caption='Your Enhanced Image', use_column_width=True) # Output Image
                output_image_size_kb = get_file_size(latest_file)
                if output_image_size_kb:
                    st.write(f"Your Enhanced Image Size: {output_image_size_kb:.2f} KB") # Output Image Size
                
        # Add completion message to chat history
        chat_history.append(("System", "This is your image with high resolution...", latest_file)) # Super-resolution completed successfully.
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Display chat history
st.header("Chat History")
for msg in chat_history:
    if msg[0] == "User":
        st.write(f"{msg[0]} {msg[1]}")
        st.image(msg[2], caption='Your Image', use_column_width=True) # Uploaded Image
    else:
        st.write(msg[1])
        if msg[2]:
            st.image(msg[2], caption='Your Enhanced Image', use_column_width=True) # Output Image
            output_image_size_kb = get_file_size(msg[2])
            if output_image_size_kb:
                st.write(f"High Resolution Image Size: {output_image_size_kb:.2f} KB") # Output Image Size
