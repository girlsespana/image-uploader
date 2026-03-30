from PIL import Image, ImageDraw, ImageFont
import threading


WATERMARK_TEXT = "G I R L S E S . C O M"
lock = threading.Lock()


def apply_watermark(image_path: str) -> str:
    """
    Apply watermark to an image and save it back to the same path.

    Args:
        image_path: Path to the image file

    Returns:
        str: Path to the watermarked image (same as input)
    """
    with lock:
        img = Image.open(image_path).convert("RGBA")
        W, H = img.size

        # Create text layer
        txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)

        target_width = W * 1.1
        estimated_size = int(W / 7)

        # Try to load Arial font, fall back to default
        try:
            font = ImageFont.truetype("arial.ttf", estimated_size)
        except:
            font = ImageFont.load_default(estimated_size)

        text_w, text_h = draw.textbbox((0, 0), WATERMARK_TEXT, font=font)[2:]

        # Ensure text is slightly larger than target width
        if text_w < target_width:
            scale_factor = target_width / text_w
            estimated_size = int(estimated_size * scale_factor)

            try:
                font = ImageFont.truetype("arial.ttf", estimated_size)
            except:
                font = ImageFont.load_default()

            text_w, text_h = draw.textbbox((0, 0), WATERMARK_TEXT, font=font)[2:]

        padding = 40

        # Create watermark layer with padding
        watermark_layer = Image.new(
            "RGBA",
            (text_w + padding * 2, text_h + padding * 2),
            (255, 255, 255, 0)
        )
        wm_draw = ImageDraw.Draw(watermark_layer)

        # Draw text with 50% opacity black
        wm_draw.text(
            (padding, padding),
            WATERMARK_TEXT,
            font=font,
            fill=(0, 0, 0, 50)
        )

        # Rotate 45 degrees
        rotated = watermark_layer.rotate(45, expand=True)

        # Center the watermark
        pos = ((W - rotated.width) // 2, (H - rotated.height) // 2)

        # Composite watermark onto original image
        img.alpha_composite(rotated, pos)

        # Determine output format based on original extension
        ext = image_path.split(".")[-1].lower()
        if ext in ["jpg", "jpeg"]:
            img.convert("RGB").save(image_path, format="JPEG", quality=85)
        elif ext == "png":
            img.convert("RGB").save(image_path, format="PNG")
        else:
            img.convert("RGB").save(image_path, format="JPEG", quality=85)

        return image_path
