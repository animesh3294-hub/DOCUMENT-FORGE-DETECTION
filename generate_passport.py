from PIL import Image, ImageDraw, ImageFont

def create_test_passport(filename, line2_text, is_valid_math):
    # Create a blank white document canvas
    img = Image.new('RGB', (900, 450), color='white')
    d = ImageDraw.Draw(img)

    # Mock passport header text
    d.text((50, 40), "REPUBLIC OF INDIA", fill=(0, 0, 0))
    d.text((50, 80), "PASSPORT", fill=(0, 0, 0))
    d.text((50, 130), "Name: AMAN GAUTAM", fill=(0, 0, 0))
    d.text((50, 170), "Nationality: IND", fill=(0, 0, 0))

    # Standard ICAO 9303 MRZ lines
    mrz_line1 = "P<INDGAUTAM<<AMAN<<<<<<<<<<<<<<<<<<<<<<<<<<"
    
    # Draw MRZ at the bottom
    d.text((50, 330), mrz_line1, fill=(0, 0, 0))
    d.text((50, 370), line2_text, fill=(0, 0, 0))
    
    img.save(filename)
    print(f"Generated {filename} (Math Valid: {is_valid_math})")

# 1. Valid MRZ line 2 (Correct check digit '0' at the end)
create_test_passport(
    "test_passport_valid.png", 
    "J8369854<4IND0904128M3604126<<<<<<<<<<<<<<0", 
    True
)

# 2. Forged/Tampered MRZ line 2 (Broken check digit '9' at the end instead of '0')
create_test_passport(
    "test_passport_invalid.png", 
    "J8369854<4IND0904128M3604126<<<<<<<<<<<<<<9", 
    False
)