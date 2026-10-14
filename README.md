# DCT Image Steganography

A Python-based image steganography application that hides secret text messages inside grayscale images using the Discrete Cosine Transform (DCT).

## Features
- Embed secret text into an image using 8×8 DCT blocks.
- Extract hidden messages from stego images.
- Download the generated image in PNG format.
- Calculate Mean Squared Error (MSE) and Peak Signal-to-Noise Ratio (PSNR).
- View image differences and message capacity.
- Interactive web interface built with Streamlit.

## Technologies
- Python
- OpenCV
- NumPy
- Streamlit

## Installation

1. Clone this repository.
2. Install the dependencies:

   `pip install -r requirements.txt`

3. Run the application:

   `streamlit run app.py`

## How It Works

The application converts an image to grayscale, processes it in 8×8 blocks, and modifies a selected DCT coefficient to represent each message bit. The same technique is used to extract the hidden text.

## Academic Project

Developed as a Digital Image Processing semester project. This is an educational demonstration and does not provide message encryption.