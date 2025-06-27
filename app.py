import os
import io
from flask import Flask, render_template, request, flash, send_file
from werkzeug.utils import secure_filename
import steganography

app = Flask(__name__)
app.secret_key = os.urandom(24) # Kunci rahasia aman untuk produksi

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'bmp', 'jpg', 'jpeg'}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files or request.files['image'].filename == '':
            flash('Tidak ada file yang dipilih')
            return render_template('index.html')
        
        file = request.files['image']
        if not allowed_file(file.filename):
            flash('Format file tidak diizinkan')
            return render_template('index.html')

        # Logika Encode
        if 'encode' in request.form:
            secret_text = request.form['secret_text']
            if not secret_text:
                flash('Teks rahasia tidak boleh kosong!')
                return render_template('index.html')

            image_bytes = file.read()
            encoded_buffer, message = steganography.encode_image(image_bytes, secret_text)
            
            flash(message)
            if encoded_buffer:
                return send_file(
                    encoded_buffer,
                    mimetype='image/png',
                    as_attachment=True,
                    download_name=f'encoded_{os.path.splitext(file.filename)[0]}.png'
                )
            return render_template('index.html')

        # Logika Decode
        elif 'decode' in request.form:
            filename = secure_filename(file.filename)
            temp_dir = '/tmp' # Vercel hanya mengizinkan penulisan di folder /tmp
            filepath = os.path.join(temp_dir, filename)
            file.save(filepath)
            
            decoded_text = steganography.decode_image(filepath)
            os.remove(filepath) # Hapus file sementara setelah selesai
            return render_template('index.html', decoded_text=decoded_text)

    return render_template('index.html')