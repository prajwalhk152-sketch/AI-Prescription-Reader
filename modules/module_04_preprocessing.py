import streamlit as st
import os
import cv2
import numpy as np
from PIL import Image
from datetime import datetime

INPUT_DIR = "outputs/module_03_upload"
OUTPUT_DIR = "outputs/module_04_preprocessed"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_uploaded_images():
    if not os.path.exists(INPUT_DIR):
        return []

    allowed_extensions = [".jpg", ".jpeg", ".png"]
    files = []

    for file in os.listdir(INPUT_DIR):
        file_path = os.path.join(INPUT_DIR, file)

        if os.path.isfile(file_path):
            if os.path.splitext(file)[1].lower() in allowed_extensions:
                files.append(file)

    return sorted(files, reverse=True)


def preprocess_image(image_path, apply_gray, apply_noise, apply_contrast, apply_threshold, handwriting_enhancement=False):
    image = cv2.imread(image_path)

    if image is None:
        return None, None, None, None

    if handwriting_enhancement:
        height, width = image.shape[:2]
        if width < 1800:
            scale = 1800 / width
            image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    original_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    processed = image.copy()

    grayscale_image = None
    noise_removed_image = None
    contrast_image = None
    threshold_image = None

    if apply_gray:
        processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
        grayscale_image = processed.copy()

    if apply_noise:
        if len(processed.shape) == 3:
            processed = cv2.medianBlur(processed, 3)
        else:
            processed = cv2.medianBlur(processed, 3)
        noise_removed_image = processed.copy()

    if apply_contrast:
        if len(processed.shape) == 3:
            lab = cv2.cvtColor(processed, cv2.COLOR_BGR2LAB)
            l_channel, a_channel, b_channel = cv2.split(lab)

            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced_l = clahe.apply(l_channel)

            merged = cv2.merge((enhanced_l, a_channel, b_channel))
            processed = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
            contrast_image = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
        else:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            processed = clahe.apply(processed)
            contrast_image = processed.copy()

    if apply_threshold:
        if len(processed.shape) == 3:
            processed_gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
        else:
            processed_gray = processed

        if handwriting_enhancement:
            processed_gray = cv2.fastNlMeansDenoising(processed_gray, None, 18, 7, 21)
            processed_gray = cv2.addWeighted(
                processed_gray,
                1.55,
                cv2.GaussianBlur(processed_gray, (0, 0), 1.2),
                -0.55,
                0
            )
            processed = cv2.adaptiveThreshold(
                processed_gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                31,
                9
            )
            inverted = cv2.bitwise_not(processed)
            repaired = cv2.morphologyEx(
                inverted,
                cv2.MORPH_CLOSE,
                cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)),
                iterations=1
            )
            processed = cv2.bitwise_not(repaired)
            threshold_image = processed.copy()
            return original_rgb, grayscale_image, noise_removed_image, contrast_image, threshold_image

        processed = cv2.adaptiveThreshold(
            processed_gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )

        threshold_image = processed.copy()

    return original_rgb, grayscale_image, noise_removed_image, contrast_image, threshold_image


def show_module_04_preprocessing():
    st.title("Image Preprocessing using OpenCV")

    st.write(
        "It improves prescription image quality before OCR. "
        "It applies grayscale conversion, noise removal, contrast enhancement, "
        "and thresholding."
    )

    uploaded_images = get_uploaded_images()

    if not uploaded_images:
        st.warning(
            "No uploaded image found. Please complete  uploading JPG, JPEG, or PNG file."
        )
        return

    selected_image = st.selectbox(
        "Select uploaded prescription image",
        uploaded_images
    )

    image_path = os.path.join(INPUT_DIR, selected_image)

    st.subheader("Original Uploaded Image")
    st.image(image_path, caption=selected_image, width=320)

    st.subheader("Choose Preprocessing Actions")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        apply_gray = st.checkbox("Grayscale", value=True)

    with col2:
        apply_noise = st.checkbox("Noise Removal", value=True)

    with col3:
        apply_contrast = st.checkbox("Contrast Enhancement", value=True)

    with col4:
        apply_threshold = st.checkbox("Thresholding", value=True)

    handwriting_enhancement = st.checkbox(
        "Handwriting enhancement",
        value=True,
        help="Upscales and repairs faint handwritten strokes before OCR."
    )

    if st.button("Preprocess Image"):
        (
            original_rgb,
            grayscale_image,
            noise_removed_image,
            contrast_image,
            threshold_image
        ) = preprocess_image(
            image_path,
            apply_gray,
            apply_noise,
            apply_contrast,
            apply_threshold,
            handwriting_enhancement
        )

        if original_rgb is None:
            st.error("Unable to read image.")
            return

        st.success("Image preprocessing completed successfully.")

        st.subheader("Preprocessing Outputs")

        tabs = st.tabs(
            [
                "Original",
                "Grayscale",
                "Noise Removed",
                "Contrast Enhanced",
                "Final Threshold Output"
            ]
        )

        with tabs[0]:
            st.image(original_rgb, caption="Original Image", width=420)

        with tabs[1]:
            if grayscale_image is not None:
                st.image(grayscale_image, caption="Grayscale Image", width=420)
            else:
                st.info("Grayscale was not selected.")

        with tabs[2]:
            if noise_removed_image is not None:
                st.image(noise_removed_image, caption="Noise Removed Image", width=420)
            else:
                st.info("Noise removal was not selected.")

        with tabs[3]:
            if contrast_image is not None:
                st.image(contrast_image, caption="Contrast Enhanced Image", width=420)
            else:
                st.info("Contrast enhancement was not selected.")

        with tabs[4]:
            if threshold_image is not None:
                st.image(threshold_image, caption="Final Threshold Image", width=420)
                final_output = threshold_image
            else:
                st.warning("Thresholding was not selected. Saving contrast/noise/grayscale result.")
                if contrast_image is not None:
                    final_output = contrast_image
                elif noise_removed_image is not None:
                    final_output = noise_removed_image
                elif grayscale_image is not None:
                    final_output = grayscale_image
                else:
                    final_output = original_rgb

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file_name = f"preprocessed_{timestamp}.png"
        output_path = os.path.join(OUTPUT_DIR, output_file_name)

        if len(final_output.shape) == 3:
            final_bgr = cv2.cvtColor(final_output, cv2.COLOR_RGB2BGR)
            cv2.imwrite(output_path, final_bgr)
        else:
            cv2.imwrite(output_path, final_output)

        st.subheader("Preprocessing Output")

        st.success("Preprocessed image saved successfully.")
        st.write("**Saved File:**", output_file_name)
        st.write("**Saved Path:**", output_path)

        st.info(
            "This preprocessed image is ready for OCR text extraction: OCR Text Extraction."
        )
