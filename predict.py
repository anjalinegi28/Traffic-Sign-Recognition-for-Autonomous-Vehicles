import cv2
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from tensorflow import keras

model = keras.models.load_model("traffic_sign_recognition_model.keras")
with open("class_names.json", "r") as f:
    CLASS_NAMES = json.load(f)

# ---- Global style ----
plt.rcParams["font.family"] = "DejaVu Sans"

# Warm, light beige theme with dark, high-contrast text
BAR_COLORS = ["#2E7D32", "#1565C0", "#8E24AA", "#D81B60", "#EF6C00"]
BG_COLOR = "#F5EDE1"       # light beige page background
PANEL_COLOR = "#FBF6EC"    # slightly lighter panel background
TEXT_COLOR = "#2B2621"     # near-black warm text (high contrast on beige)
GRID_COLOR = "#C9BFA9"     # soft beige-brown gridlines
ACCENT = "#B3541E"         # warm brown/terracotta accent


def predict_sign(image_path, top_k=3):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Could not read image: {image_path}")
        return

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (32, 32))
    img_norm = img_resized.astype(np.float32) / 255.0
    img_batch = np.expand_dims(img_norm, axis=0)

    probs = model.predict(img_batch, verbose=0)[0]
    top_indices = np.argsort(probs)[::-1][:top_k]

    print(f"\nImage: {image_path}")
    print(f"Prediction  : {CLASS_NAMES[top_indices[0]]}")
    print(f"Confidence  : {probs[top_indices[0]] * 100:.2f}%")
    print(f"\nTop {top_k} results:")
    for i, idx in enumerate(top_indices):
        print(f"  #{i+1}  {CLASS_NAMES[idx]:<40} {probs[idx] * 100:.2f}%")

    # ---- Figure setup ----
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), facecolor=BG_COLOR)
    for ax in axes:
        ax.set_facecolor(PANEL_COLOR)

    # ---- Left panel: input image ----
    axes[0].imshow(img_rgb)
    axes[0].set_title("Input Image", fontsize=13, color=TEXT_COLOR, fontweight="bold", pad=12)
    axes[0].axis("off")
    for spine in axes[0].spines.values():
        spine.set_visible(False)

    # Add a clear border frame around the image
    rect = plt.Rectangle(
        (0, 0), 1, 1, transform=axes[0].transAxes,
        fill=False, edgecolor=ACCENT, linewidth=2.5
    )
    axes[0].add_patch(rect)

    # ---- Right panel: bar chart ----
    bar_labels = [CLASS_NAMES[i][:28] for i in top_indices]
    bar_values = [probs[i] * 100 for i in top_indices]
    colors = BAR_COLORS[:top_k][::-1]

    bars = axes[1].barh(
        bar_labels[::-1], bar_values[::-1],
        color=colors, edgecolor="none", height=0.55,
        zorder=3
    )

    axes[1].set_xlabel("Confidence (%)", color=TEXT_COLOR, fontsize=11, fontweight="bold")
    axes[1].set_title(f"Top-{top_k} Predictions", fontsize=13, color=TEXT_COLOR, fontweight="bold", pad=12)
    axes[1].set_xlim(0, 108)
    axes[1].tick_params(colors=TEXT_COLOR, labelsize=10)
    axes[1].set_yticklabels(bar_labels[::-1], color=TEXT_COLOR, fontsize=10, fontweight="medium")
    axes[1].grid(axis="x", color=GRID_COLOR, linestyle="--", linewidth=0.8, zorder=0)
    for spine in axes[1].spines.values():
        spine.set_visible(False)

    for i, v in enumerate(bar_values[::-1]):
        axes[1].text(
            v + 2, i, f"{v:.1f}%",
            va="center", fontsize=10, color=TEXT_COLOR, fontweight="bold"
        )

    fig.suptitle(
        f"Predicted: {CLASS_NAMES[top_indices[0]]}",
        fontsize=16, fontweight="bold", color=ACCENT, y=0.99
    )
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plt.show()


import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()
image_path = filedialog.askopenfilename(
    title="Select a traffic sign image",
    filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.ppm")]
)
if image_path:
    predict_sign(image_path)
else:
    print("No image selected.")