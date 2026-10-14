import streamlit as st
import cv2
import numpy as np

st.set_page_config(
    page_title="DCT Image Steganography",
    page_icon="🔐",
    layout="wide"
)

st.title("🔐 DCT Image Steganography")
st.write(
    "Hide and extract secret messages using "
    "Discrete Cosine Transform (DCT)."
)


# ============================================================
# DCT EMBEDDING
# ============================================================

def embed_message(img, message):
    bits = ''.join(format(ord(char), '08b') for char in message)

    height, width = img.shape
    capacity = (height // 8) * (width // 8)

    if len(bits) > capacity:
        return None

    stego = img.copy()
    bit_index = 0

    for i in range(0, height, 8):
        for j in range(0, width, 8):
            if bit_index >= len(bits):
                break

            block = np.float32(img[i:i+8, j:j+8])
            dct_block = cv2.dct(block)

            dct_block[3, 4] = (
                6 if bits[bit_index] == '1' else -6
            )

            stego_block = cv2.idct(dct_block)
            stego[i:i+8, j:j+8] = np.clip(
                stego_block, 0, 255
            ).astype(np.uint8)

            bit_index += 1

        if bit_index >= len(bits):
            break

    return stego


# ============================================================
# DCT EXTRACTION
# ============================================================

def extract_message(stego, message_length):
    bits = ""
    height, width = stego.shape
    total_bits = message_length * 8
    capacity = (height // 8) * (width // 8)

    if total_bits > capacity:
        return None

    bit_index = 0

    for i in range(0, height, 8):
        for j in range(0, width, 8):
            if bit_index >= total_bits:
                break

            block = np.float32(stego[i:i+8, j:j+8])
            dct_block = cv2.dct(block)

            bits += '1' if dct_block[3, 4] > 0 else '0'
            bit_index += 1

        if bit_index >= total_bits:
            break

    message = ""

    for i in range(0, len(bits), 8):
        message += chr(int(bits[i:i+8], 2))

    return message


# ============================================================
# IMAGE QUALITY
# ============================================================

def calculate_mse(original, stego):
    difference = (
        original.astype(np.float32)
        - stego.astype(np.float32)
    )
    return float(np.mean(difference ** 2))


def calculate_psnr(mse):
    if mse == 0:
        return float("inf")
    return float(10 * np.log10((255 ** 2) / mse))


def prepare_image(file_bytes):
    image = cv2.imdecode(
        np.frombuffer(file_bytes, dtype=np.uint8),
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        return None

    height, width = image.shape
    height = (height // 8) * 8
    width = (width // 8) * 8

    if height == 0 or width == 0:
        return None

    return image[:height, :width]


# ============================================================
# TABS
# ============================================================

hide_tab, extract_tab, about_tab, test_tab = st.tabs([
    "🔒 Hide Message",
    "🔓 Extract Message",
    "ℹ️ About Project",
    "🧪 Testing & Validation"
])


# ============================================================
# HIDE MESSAGE
# ============================================================

with hide_tab:
    st.header("🔒 Hide a Secret Message")

    uploaded_file = st.file_uploader(
        "Upload Cover Image",
        type=["jpg", "jpeg", "png"],
        key="hide_image"
    )

    if uploaded_file:
        img = prepare_image(uploaded_file.getvalue())

        if img is None:
            st.error("Unable to read this image.")
        else:
            height, width = img.shape
            capacity = (height // 8) * (width // 8)
            capacity_chars = capacity // 8

            col1, col2 = st.columns(2)

            with col1:
                st.image(
                    img,
                    caption="Cover Image",
                    use_container_width=True
                )

            with col2:
                st.metric("Image Width", f"{width} px")
                st.metric("Image Height", f"{height} px")
                st.metric("Capacity", f"{capacity_chars} characters")

            message = st.text_area(
                "Enter secret message",
                placeholder="Example: DCT STEGANOGRAPHY",
                key="secret_message"
            )

            required_bits = len(message) * 8
            usage = required_bits / capacity if capacity else 0

            st.subheader("📊 Message Capacity")

            col1, col2, col3 = st.columns(3)

            col1.metric("Maximum Characters", capacity_chars)
            col2.metric("Message Characters", len(message))
            col3.metric("Bits Required", f"{required_bits}/{capacity}")

            st.progress(min(usage, 1.0))

            if required_bits > capacity:
                st.error("Message is too large for this image.")
            elif message:
                st.success(f"Capacity available: {usage * 100:.2f}% used")

            if st.button(
                "🔐 Hide Message",
                type="primary",
                key="hide_button"
            ):
                if not message:
                    st.warning("Enter a message first.")
                elif required_bits > capacity:
                    st.error("Message is too large.")
                else:
                    stego = embed_message(img, message)

                    if stego is not None:
                        st.session_state["last_stego"] = stego
                        st.session_state["last_original"] = img
                        st.session_state["last_message"] = message

                        st.success("Message embedded successfully!")

            if "last_stego" in st.session_state:
                stego = st.session_state["last_stego"]
                original = st.session_state["last_original"]

                st.divider()
                st.subheader("🖼️ Stego Image")

                st.image(
                    stego,
                    caption="Image containing hidden message",
                    use_container_width=True
                )

                success, buffer = cv2.imencode(".png", stego)

                if success:
                    st.download_button(
                        "⬇️ Download Stego PNG",
                        data=buffer.tobytes(),
                        file_name="stego_image.png",
                        mime="image/png"
                    )

                mse = calculate_mse(original, stego)
                psnr = calculate_psnr(mse)
                max_diff = int(np.max(cv2.absdiff(original, stego)))

                st.divider()
                st.subheader("📈 Image Quality Analysis")

                col1, col2, col3 = st.columns(3)
                col1.metric("MSE", f"{mse:.6f}")
                col2.metric("PSNR", f"{psnr:.2f} dB")
                col3.metric("Max Pixel Difference", max_diff)

                st.subheader("🔍 Difference Image")

                st.image(
                    cv2.absdiff(original, stego),
                    caption="Pixel differences",
                    use_container_width=True
                )


# ============================================================
# EXTRACT MESSAGE
# ============================================================

with extract_tab:
    st.header("🔓 Extract Secret Message")

    stego_file = st.file_uploader(
        "Upload Stego PNG",
        type=["png", "jpg", "jpeg"],
        key="extract_image"
    )

    if stego_file:
        stego = prepare_image(stego_file.getvalue())

        if stego is None:
            st.error("Unable to read this image.")
        else:
            height, width = stego.shape
            capacity_chars = ((height // 8) * (width // 8)) // 8

            st.image(
                stego,
                caption="Uploaded Stego Image",
                use_container_width=True
            )

            message_length = st.number_input(
                "Original message length (characters)",
                min_value=1,
                max_value=max(1, capacity_chars),
                step=1
            )

            if st.button(
                "🔓 Extract Message",
                type="primary",
                key="extract_button"
            ):
                extracted = extract_message(stego, int(message_length))

                if extracted is None:
                    st.error("Message length exceeds image capacity.")
                else:
                    st.success("Extraction process completed.")
                    st.text_area(
                        "Extracted Message",
                        value=extracted,
                        height=120
                    )


# ============================================================
# ABOUT PROJECT
# ============================================================

with about_tab:
    st.header("ℹ️ About the Project")

    st.markdown("""
    ### DCT Image Steganography

    This academic project hides secret text inside a grayscale image
    using the Discrete Cosine Transform.

    **Technologies:** Python, OpenCV, NumPy and Streamlit.
    """)

    st.subheader("⚙️ How It Works")

    st.markdown("""
    1. Upload a cover image.
    2. Convert it to grayscale.
    3. Divide it into 8×8 blocks.
    4. Apply DCT to each block.
    5. Convert the message to binary.
    6. Embed one bit in coefficient `DCT[3,4]`.
    7. Apply inverse DCT.
    8. Save the resulting stego image as PNG.
    9. Recover the bits by checking coefficient signs.
    """)

    st.divider()
    st.subheader("🔄 Message Embedding Workflow")

    st.code("""
Cover Image + Secret Message
             |
             v
       Grayscale Image
             |
             v
      Divide into 8×8 Blocks
             |
             v
            DCT
             |
             v
      Embed Bits at DCT[3,4]
             |
             v
            IDCT
             |
             v
        Stego Image
    """, language="text")

    st.subheader("🔄 Message Extraction Workflow")

    st.code("""
        Stego Image
             |
             v
      Divide into 8×8 Blocks
             |
             v
            DCT
             |
             v
      Read Coefficient Sign
             |
             v
      Recover Binary Bits
             |
             v
        Convert to Text
             |
             v
       Secret Message
    """, language="text")

    st.divider()
    st.subheader("🧠 Embedding Rule")

    st.code("""
Bit 1 -> DCT[3,4] = +6
Bit 0 -> DCT[3,4] = -6
    """, language="text")

    st.subheader("📊 Quality Metrics")

    st.markdown("""
    - **MSE:** Average squared pixel difference; lower generally means less distortion.
    - **PSNR:** Image quality measure; higher generally means less distortion.
    """)

    st.warning(
        "Academic demonstration only. This method is not production-grade "
        "secure steganography and does not encrypt the secret message."
    )


# ============================================================
# DAY 44: TESTING & VALIDATION
# ============================================================

with test_tab:
    st.header("🧪 Testing & Validation")

    st.write(
        "Use this checklist to record whether the application "
        "passes each test. Run the tests using the Hide and Extract tabs."
    )

    tests = [
        (
            "Test 1 — Short message",
            "Hide and extract HI. Confirm the recovered text is exactly HI."
        ),
        (
            "Test 2 — Longer message",
            "Hide and extract DCT STEGANOGRAPHY. Confirm the text matches."
        ),
        (
            "Test 3 — Capacity validation",
            "Enter a message longer than the displayed capacity. Confirm the warning appears."
        ),
        (
            "Test 4 — Empty message",
            "Click Hide Message without entering text. Confirm a warning appears."
        ),
        (
            "Test 5 — Image quality",
            "After embedding, confirm MSE, PSNR and Difference Image are displayed."
        ),
        (
            "Test 6 — Saved PNG",
            "Download the stego PNG, upload it in Extract Message, and verify the text."
        )
    ]

    st.caption(
        "Mark a test as passed only after you have performed it."
    )

    for index, (title, description) in enumerate(tests):
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(description)
            st.checkbox(
                "Passed",
                key=f"test_passed_{index}"
            )

    passed = sum(
        st.session_state.get(f"test_passed_{i}", False)
        for i in range(len(tests))
    )

    st.divider()
    st.subheader("📋 Test Summary")

    col1, col2 = st.columns(2)

    col1.metric("Tests Passed", f"{passed}/{len(tests)}")
    col2.metric(
        "Remaining",
        len(tests) - passed
    )

    st.progress(passed / len(tests))

    if passed == len(tests):
        st.success(
            "All checklist items are marked passed. "
            "Make sure each test was actually performed."
        )
    else:
        st.info("Complete the remaining tests to finish validation.")

