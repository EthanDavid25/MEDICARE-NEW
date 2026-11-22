"""
Generate professional MEDICARE mobile brand assets for Expo SDK 52.
Assets required:
- mobile/assets/icon.png (1024x1024)
- mobile/assets/adaptive-icon.png (1024x1024)
- mobile/assets/splash-icon.png (1024x1024)
- mobile/assets/favicon.png (48x48)
"""
import os
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mobile", "assets"))
os.makedirs(ASSETS_DIR, exist_ok=True)

# Theme Colors
NAVY_BG = (10, 35, 66)       # #0A2342
WHITE = (255, 255, 255)
ACCENT_BLUE = (37, 99, 235)  # #2563EB
RED_CROSS = (220, 38, 38)    # #DC2626
TRANSPARENT = (0, 0, 0, 0)

def draw_medical_cross(draw, center_x, center_y, size, color):
    """Draws a proportional medical cross emblem."""
    arm_thickness = size // 3
    half_size = size // 2
    half_thickness = arm_thickness // 2

    # Horizontal bar
    draw.rectangle([
        center_x - half_size, center_y - half_thickness,
        center_x + half_size, center_y + half_thickness
    ], fill=color)

    # Vertical bar
    draw.rectangle([
        center_x - half_thickness, center_y - half_size,
        center_x + half_thickness, center_y + half_size
    ], fill=color)

def generate_icon():
    img = Image.new("RGBA", (1024, 1024), NAVY_BG)
    draw = ImageDraw.Draw(img)

    # White shield / rounded container in center
    badge_radius = 360
    center = 512
    draw.ellipse([
        center - badge_radius, center - badge_radius,
        center + badge_radius, center + badge_radius
    ], fill=WHITE, outline=ACCENT_BLUE, width=16)

    # Draw vibrant medical cross
    draw_medical_cross(draw, center, center, 420, RED_CROSS)

    output_path = os.path.join(ASSETS_DIR, "icon.png")
    img.save(output_path, "PNG")
    print(f"Generated: {output_path} (1024x1024)")

def generate_adaptive_icon():
    # Adaptive icon foreground is typically drawn on transparent or clean canvas
    # The inner 66% (approx 660px) is the safe mask zone
    img = Image.new("RGBA", (1024, 1024), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    center = 512
    badge_radius = 280

    # Circular white backing
    draw.ellipse([
        center - badge_radius, center - badge_radius,
        center + badge_radius, center + badge_radius
    ], fill=WHITE, outline=ACCENT_BLUE, width=12)

    # Medical cross emblem
    draw_medical_cross(draw, center, center, 320, RED_CROSS)

    output_path = os.path.join(ASSETS_DIR, "adaptive-icon.png")
    img.save(output_path, "PNG")
    print(f"Generated: {output_path} (1024x1024)")

def generate_splash_icon():
    img = Image.new("RGBA", (1024, 1024), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    center_x = 512
    center_y = 512
    badge_radius = 240

    # Circular white backing
    draw.ellipse([
        center_x - badge_radius, center_y - badge_radius,
        center_x + badge_radius, center_y + badge_radius
    ], fill=WHITE, outline=ACCENT_BLUE, width=12)

    # Medical cross
    draw_medical_cross(draw, center_x, center_y, 280, RED_CROSS)

    output_path = os.path.join(ASSETS_DIR, "splash-icon.png")
    img.save(output_path, "PNG")
    print(f"Generated: {output_path} (1024x1024)")

def generate_favicon():
    img = Image.new("RGBA", (48, 48), NAVY_BG)
    draw = ImageDraw.Draw(img)

    # Small circular badge
    draw.ellipse([6, 6, 42, 42], fill=WHITE)
    draw_medical_cross(draw, 24, 24, 22, RED_CROSS)

    output_path = os.path.join(ASSETS_DIR, "favicon.png")
    img.save(output_path, "PNG")
    print(f"Generated: {output_path} (48x48)")

if __name__ == "__main__":
    generate_icon()
    generate_adaptive_icon()
    generate_splash_icon()
    generate_favicon()
    print("All mobile assets generated successfully!")
