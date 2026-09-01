from PIL import Image, ImageDraw, ImageFont

def create_true_hd_passport(filename, line2_text):
    # Create a large high-res canvas directly
    img = Image.new('RGB', (1200, 600), color='#f4f4f9')
    d = ImageDraw.Draw(img)

    # Load a smooth, real system font (Consolas is perfect for OCR)
    try:
        font = ImageFont.truetype("consola.ttf", 40)
    except IOError:
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            font = ImageFont.load_default()

    # Draw the text smoothly
    d.text((60, 60), "REPUBLIC OF INDIA - PASSPORT", fill=(0, 0, 0), font=font)
    d.text((60, 150), "Name: AMAN GAUTAM", fill=(0, 0, 0), font=font)
    d.text((60, 210), "Nationality: IND", fill=(0, 0, 0), font=font)

    # Standard ICAO MRZ
    d.text((60, 420), "P<INDGAUTAM<<AMAN<<<<<<<<<<<<<<<<<<<<<<<<<<", fill=(0, 0, 0), font=font)
    d.text((60, 480), line2_text, fill=(0, 0, 0), font=font)
    
    img.save(filename)
    print(f"✅ Generated True HD {filename}")

# Valid Passport: The mathematical check digit for L8888888< is 7.
create_true_hd_passport("perfect_passport_valid.png", "L8888888<7IND0904128M3604126<<<<<<<<<<<<<<0")

# Forged Passport: We tampered with the check digit, changing the 7 to a 2.
create_true_hd_passport("perfect_passport_forged.png", "L8888888<2IND0904128M3604126<<<<<<<<<<<<<<0")