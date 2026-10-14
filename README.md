# DCT Image Steganography

A Digital Image Processing project that hides secret text messages inside grayscale images using the Discrete Cosine Transform (DCT).

## Features

- Embed secret text into images using 8×8 DCT blocks.
- Extract hidden messages from stego images.
- Download the output image as PNG.
- Calculate Mean Squared Error (MSE) and Peak Signal-to-Noise Ratio (PSNR).
- View image differences and message capacity.
- Interactive Streamlit web interface.

## Technologies Used

- Python
- OpenCV
- NumPy
- Streamlit

## Installation and Usage

1. Install Python.
2. Open a terminal in the project folder.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   streamlit run app.py
   ```

## How It Works

The application converts the cover image to grayscale and divides it into 8×8 blocks. It modifies a selected DCT coefficient to represent message bits and uses the same technique to extract the hidden text.

## Evaluation

Image quality is evaluated using MSE, PSNR, and pixel-difference measurements.

## Academic Project

Developed as a semester project for Digital Image Processing.

**Note:** This is an educational demonstration. It does not encrypt the secret message.