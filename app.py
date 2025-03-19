from flask import Flask, render_template, request, send_file, url_for
import qrcode
from io import BytesIO
import os
import tempfile

app = Flask(__name__)

# Create a temporary directory to store QR codes
TEMP_DIR = tempfile.mkdtemp()
@app.route('/about')
def about():
    return render_template('About.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    qr_code_url = None  # Will store the URL of the generated QR code
    download_url = None  # URL to download the generated QR code

    if request.method == 'POST':
        url = request.form.get('url')
        fill_color = request.form.get('fill_color')
        back_color = request.form.get('back_color')

        # Generate QR code with user inputs
        img = generate_qr(url, fill_color, back_color)

        # Save the image in a temporary file and return it as a response
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)

        # Save the image to a temporary file for download
        temp_filename = os.path.join(TEMP_DIR, "qr_code.png")
        with open(temp_filename, 'wb') as f:
            f.write(img_io.read())

        # Generate URL for the image (viewing or downloading)
        qr_code_url = url_for('generate_qr_code')  # Use the route for viewing the image
        download_url = url_for('download_qr_code')  # Use the route for downloading the image

    return render_template('index.html', qr_code_url=qr_code_url, download_url=download_url)


@app.route('/generate_qr_code')
def generate_qr_code():
    if os.path.exists(os.path.join(TEMP_DIR, "qr_code.png")):
        return send_file(os.path.join(TEMP_DIR, "qr_code.png"), mimetype='image/png')
    return "QR Code not found", 404


@app.route('/download_qr_code')
def download_qr_code():
    temp_filename = os.path.join(TEMP_DIR, "qr_code.png")
    if os.path.exists(temp_filename):
        # Provide the image for download
        return send_file(temp_filename, as_attachment=True, download_name='qr_code.png', mimetype='image/png')
    return "QR Code not found", 404


def generate_qr(url, fill_color, back_color):
    # Create QRCode instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )

    # Add data to the QRCode
    qr.add_data(url)
    qr.make(fit=True)

    # Generate the QR code image with custom colors
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    return img

@app.route('/download_report')
def download_report():
    # Define the path to the report PDF file in the static folder
    report_path = os.path.join(app.root_path, 'static', 'Report.pdf')
    
    # Ensure the file exists before sending
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True, download_name='Report.pdf', mimetype='application/pdf')
    return "Report not found", 404


if __name__ == "__main__":
    app.run(debug=True)
