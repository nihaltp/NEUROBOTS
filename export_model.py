"""
Download the MobileNetV2 plant disease classification model from Hugging Face
and export it to ONNX format for fast CPU inference.

Usage:
    python export_model.py
"""

import json
import os
import torch
from transformers import AutoModelForImageClassification, AutoImageProcessor

MODEL_ID = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
OUTPUT_DIR = "weights"
ONNX_PATH = os.path.join(OUTPUT_DIR, "plant_disease_classifier.onnx")
LABELS_PATH = os.path.join(OUTPUT_DIR, "labels.json")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"[1/4] Downloading model: {MODEL_ID} ...")
    model = AutoModelForImageClassification.from_pretrained(MODEL_ID)
    model.eval()
    print("      Model downloaded successfully.")

    # Save the label mapping
    labels = model.config.id2label  # {0: "Apple Scab", 1: "Apple with Black Rot", ...}
    # Ensure keys are ints for clean JSON
    labels_clean = {int(k): v for k, v in labels.items()}
    with open(LABELS_PATH, "w") as f:
        json.dump(labels_clean, f, indent=2)
    print(f"[2/4] Labels saved to {LABELS_PATH} ({len(labels_clean)} classes)")

    # Hardcode input size for MobileNetV2
    image_size = 224
    print(f"      Input size: {image_size}x{image_size}")

    # Create dummy input for export
    dummy_input = torch.randn(1, 3, image_size, image_size)

    # Export to ONNX
    print(f"[3/4] Exporting to ONNX: {ONNX_PATH} ...")
    torch.onnx.export(
        model,
        dummy_input,
        ONNX_PATH,
        input_names=["pixel_values"],
        output_names=["logits"],
        dynamic_axes={
            "pixel_values": {0: "batch_size"},
            "logits": {0: "batch_size"},
        },
        opset_version=14,
    )
    print("      ONNX export complete.")

    # Verify the ONNX model
    import onnx
    onnx_model = onnx.load(ONNX_PATH)
    onnx.checker.check_model(onnx_model)
    
    file_size_mb = os.path.getsize(ONNX_PATH) / (1024 * 1024)
    print(f"[4/4] ONNX model verified. Size: {file_size_mb:.1f} MB")
    print()
    print("Done! Update config.yaml to point to the new model:")
    print(f'  model.path: "{ONNX_PATH}"')
    print(f'  model.labels: "{LABELS_PATH}"')


if __name__ == "__main__":
    main()
