from PIL import Image

# Create a 32x32 black icon
img = Image.new("RGB", (32, 32), (0, 0, 0))  # (0,0,0) is black; change for other colors
img.save("favicon.ico")

print("✅ Favicon created successfully as 'favicon.ico'!")
