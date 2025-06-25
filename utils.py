from PIL import Image, ImageTk


def import_image(path):
    image = Image.open(path)
    resized_image = image.resize((30, 30))
    imagetk = ImageTk.PhotoImage(resized_image)
    return imagetk


def go_to_next_element(event):
    event.widget.tk_focusNext().focus()
