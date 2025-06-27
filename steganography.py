from PIL import Image
import io

def text_to_binary(text):
    return ''.join(format(ord(char), '08b') for char in text)

def encode_image(image_bytes, secret_text):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != 'RGB':
            image = image.convert('RGB')
    except Exception as e:
        return None, f"Error: Gagal membuka gambar. {e}"

    delimiter = "$$$END$$$"
    binary_secret_text = text_to_binary(secret_text + delimiter)
    
    if len(binary_secret_text) > image.width * image.height * 3:
        return None, "Error: Teks terlalu panjang."

    pixels = image.load()
    data_index = 0
    
    for y in range(image.height):
        for x in range(image.width):
            r, g, b = pixels[x, y]
            if data_index < len(binary_secret_text):
                r_bin = list(format(r, '08b')); r_bin[-1] = binary_secret_text[data_index]; r = int("".join(r_bin), 2); data_index += 1
            if data_index < len(binary_secret_text):
                g_bin = list(format(g, '08b')); g_bin[-1] = binary_secret_text[data_index]; g = int("".join(g_bin), 2); data_index += 1
            if data_index < len(binary_secret_text):
                b_bin = list(format(b, '08b')); b_bin[-1] = binary_secret_text[data_index]; b = int("".join(b_bin), 2); data_index += 1
            pixels[x, y] = (r, g, b)
            if data_index >= len(binary_secret_text): break
        if data_index >= len(binary_secret_text): break

    output_buffer = io.BytesIO()
    image.save(output_buffer, format="PNG")
    output_buffer.seek(0)
    
    return output_buffer, "Encoding berhasil."

def decode_image(image_path):
    try:
        image = Image.open(image_path)
    except Exception:
        return "Error: File gambar tidak ditemukan atau rusak."

    pixels = image.load()
    binary_data = ""
    delimiter = "$$$END$$$"
    
    for y in range(image.height):
        for x in range(image.width):
            r, g, b = pixels[x, y][:3]
            binary_data += format(r, '08b')[-1]
            binary_data += format(g, '08b')[-1]
            binary_data += format(b, '08b')[-1]

    all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
    decoded_text = ""
    for byte in all_bytes:
        if len(byte) == 8:
            decoded_text += chr(int(byte, 2))
            if decoded_text.endswith(delimiter):
                return decoded_text[:-len(delimiter)]
    
    return "Delimiter tidak ditemukan."