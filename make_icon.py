from PIL import Image, ImageDraw

img = Image.new("RGB", (512,512), "#2d89ef")

draw = ImageDraw.Draw(img)

draw.text(
    (150,200),
    "🧠",
    font=None,
    fill="white"
)

img.save("static/icons/icon.png")
