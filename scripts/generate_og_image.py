import os
import math
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont

def make_circle_mask(size):
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    return mask

def generate_clean_energy_og(bg_path, logo_path, output_path, blur_radius=14):
    W, H = 1200, 630
    
    # Load and crop background
    bg = Image.open(bg_path).convert("RGBA")
    bg_ratio = bg.width / bg.height
    target_ratio = W / H
    
    if bg_ratio > target_ratio:
        new_w = int(bg.height * target_ratio)
        offset = (bg.width - new_w) // 2
        bg = bg.crop((offset, 0, offset + new_w, bg.height))
    else:
        new_h = int(bg.width / target_ratio)
        offset = (bg.height - new_h) // 2
        bg = bg.crop((0, offset, bg.width, offset + new_h))
        
    bg = bg.resize((W, H), Image.Resampling.LANCZOS)
    
    # Apply soft aesthetic blur
    blurred = bg.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    # Slight color boost: increase saturation and contrast for rich greens
    converter = ImageEnhance.Color(blurred)
    blurred = converter.enhance(1.15)
    contrast = ImageEnhance.Contrast(blurred)
    blurred = contrast.enhance(1.05)
    
    # Create gradient overlay: Dark emerald vignette & gradient
    # Gradient from darker emerald at top/bottom to transparent in center
    gradient = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_g = ImageDraw.Draw(gradient)
    
    for y in range(H):
        # Distance from center vertical
        dy = abs(y - H / 2) / (H / 2)
        # Alpha increases toward top and bottom
        alpha = int(90 + 130 * (dy ** 1.5))
        draw_g.line([(0, y), (W, y)], fill=(6, 26, 18, alpha))
        
    # Combine background and gradient
    base = Image.alpha_composite(blurred, gradient)
    
    # Create aesthetic frosted white circular badge for the logo
    logo = Image.open(logo_path).convert("RGBA")
    
    logo_size = 230
    logo_resized = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
    
    # Center position for layout
    # Center logo slightly above midpoint to allow brand text below
    logo_cx = W // 2
    logo_cy = H // 2 - 40
    
    logo_x = logo_cx - logo_size // 2
    logo_y = logo_cy - logo_size // 2
    
    # Soft drop shadow / glow behind logo
    shadow_pad = 40
    shadow_size = logo_size + shadow_pad * 2
    shadow = Image.new("RGBA", (shadow_size, shadow_size), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    # Circle with soft blur
    s_draw.ellipse((shadow_pad, shadow_pad, shadow_size - shadow_pad, shadow_size - shadow_pad), fill=(0, 0, 0, 160))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=20))
    
    # White circular backing to ensure logo colors are perfectly vibrant and clean
    badge_pad = 8
    badge_size = logo_size + badge_pad * 2
    badge = Image.new("RGBA", (badge_size, badge_size), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(badge)
    b_draw.ellipse((0, 0, badge_size, badge_size), fill=(255, 255, 255, 250))
    
    # Paste shadow, badge, and logo onto base
    base.paste(shadow, (logo_cx - shadow_size // 2, logo_cy - shadow_size // 2 + 6), shadow)
    base.paste(badge, (logo_cx - badge_size // 2, logo_cy - badge_size // 2), badge)
    base.paste(logo_resized, (logo_x, logo_y), logo_resized)
    
    # Typography
    draw = ImageDraw.Draw(base)
    
    # Fonts
    font_bold = "C:/Windows/Fonts/segoeuib.ttf"
    font_reg = "C:/Windows/Fonts/segoeui.ttf"
    
    title_font = ImageFont.truetype(font_bold, 44) if os.path.exists(font_bold) else ImageFont.load_default()
    subtitle_font = ImageFont.truetype(font_reg, 22) if os.path.exists(font_reg) else ImageFont.load_default()
    domain_font = ImageFont.truetype(font_bold, 18) if os.path.exists(font_bold) else ImageFont.load_default()
    
    # Text 1: INDONESIA TERANG
    title_text = "INDONESIA TERANG"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    title_x = (W - title_w) // 2
    title_y = logo_y + logo_size + 24
    
    # Drop shadow for title
    draw.text((title_x + 1, title_y + 2), title_text, fill=(0, 18, 10, 200), font=title_font)
    draw.text((title_x, title_y), title_text, fill=(255, 255, 255, 255), font=title_font)
    
    # Text 2: Subtitle
    sub_text = "Komunitas, Riset & Edukasi Energi Bersih Nusantara"
    sub_bbox = draw.textbbox((0, 0), sub_text, font=subtitle_font)
    sub_w = sub_bbox[2] - sub_bbox[0]
    sub_x = (W - sub_w) // 2
    sub_y = title_y + 54
    
    draw.text((sub_x + 1, sub_y + 1), sub_text, fill=(0, 18, 10, 180), font=subtitle_font)
    draw.text((sub_x, sub_y), sub_text, fill=(210, 245, 225, 255), font=subtitle_font)
    
    # Pill Tag: indonesia-terang.id
    pill_text = "indonesia-terang.id"
    pill_bbox = draw.textbbox((0, 0), pill_text, font=domain_font)
    pill_w = pill_bbox[2] - pill_bbox[0]
    pill_h = pill_bbox[3] - pill_bbox[1]
    
    px_pad = 20
    py_pad = 8
    pw = pill_w + px_pad * 2
    ph = pill_h + py_pad * 2
    px = (W - pw) // 2
    py = sub_y + 42
    
    # Rounded pill box
    draw.rounded_rectangle((px, py, px + pw, py + ph), radius=ph//2, fill=(8, 113, 63, 220), outline=(255, 255, 255, 90), width=1)
    draw.text((px + px_pad, py + py_pad - 1), pill_text, fill=(255, 255, 255, 255), font=domain_font)
    
    # Save optimized JPEG (< 200KB for rapid WhatsApp preview)
    final_rgb = base.convert("RGB")
    final_rgb.save(output_path, "JPEG", quality=90, optimize=True)
    size_kb = os.path.getsize(output_path) / 1024
    print(f"Generated {output_path}: {W}x{H}, {size_kb:.1f} KB")

if __name__ == "__main__":
    generate_clean_energy_og(
        "public/uploads/2025/12/Project-Lisdes-1000-Titik-2.jpg",
        "public/uploads/2024/02/Logo-Indonesia-Terang.png",
        "public/og-image.jpg",
        blur_radius=12
    )
