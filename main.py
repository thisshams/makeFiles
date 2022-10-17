import os
from pickletools import optimize
from flask import Flask, flash, request, redirect, url_for, send_from_directory, send_file, render_template
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
from pylovepdf_flavor.ilovepdf import ILovePdf
import io

# pip install pymupdf
import glob
import sys
import fitz
import cv2
from fpdf import FPDF
import img2pdf


app = Flask(__name__)

# @app.route("/",methods=['GET'])
# def home():
#     return render_template('index.html')
UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = {'doc', 'docx', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return render_template("index.html")


@app.route("/BWprintPDF", methods=['GET', 'POST'])
def BWprintPDF():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            pdf = FPDF()
            # To get better resolution
            zoom_x = 2.0  # horizontal zoom
            zoom_y = 2.0  # vertical zoom
            # zoom factor 2 in each dimension
            mat = fitz.Matrix(zoom_x, zoom_y)
            tp = 0
            doc = fitz.open("uploads/"+filename)  # open document
            for page in doc:  # iterate through the pages
                pix = page.get_pixmap(matrix=mat)  # render page to an image
                pix.save("page%i.jpg" % page.number)
                tp += 1
            doc.close()
            for i in range(tp):
                img = cv2.imread(f"page{i}.jpg", 0)
                print(i)
                th, dst = cv2.threshold(img, 80, 255, cv2.THRESH_BINARY_INV)
                cv2.imwrite(f"{i}.jpg", dst)
                os.remove(f"page{i}.jpg")

            dirname = "./"
            imgs = []
            fn = os.listdir(dirname)
            fn = sorted(filter(lambda x: os.path.isfile(
                os.path.join(dirname, x)), os.listdir(dirname)))
            fn = sorted(fn, key=lambda x: int(x.replace(".jpg", ""))
                        if x.endswith(".jpg") else 999999)

            print(fn)
            for fname in fn:
                if not fname.endswith(".jpg"):
                    continue
                path = os.path.join(dirname, fname)
                if os.path.isdir(path):
                    continue
                imgs.append(path)
            with open("uploads/"+filename, "wb") as f:
                f.write(img2pdf.convert(imgs))

            for j, i in enumerate(imgs):
                os.remove(f"{j}.jpg")

            # output
            print("Successfully made pdf file")

            return_data = io.BytesIO()
            with open("uploads/"+filename, 'rb') as fo:
                return_data.write(fo.read())
                return_data.seek(0)
            try:
                print(filename)
                fileloc = os.path.join("uploads/", filename)
                os.remove(fileloc)
            except:
                print("cant delete")
            return send_file(return_data, mimetype='application/pdf',
                             download_name=filename, as_attachment=True)

    return render_template("BWprintPDF.html")


@app.route('/compressImageLossless', methods=['GET', 'POST'])
def imageCompressLossless():

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            name = filename.split(".")[0]
            img = Image.open("uploads/"+filename)
            img = ImageOps.exif_transpose(img)
            img = img.resize(img.size, Image.ANTIALIAS)
            img = img.convert("RGB")
            img.save("uploads/"+name+".jpg", optimize=True)

            return_data = io.BytesIO()
            with open("uploads/"+filename, 'rb') as fo:
                return_data.write(fo.read())
                return_data.seek(0)

            os.remove("uploads/"+filename)

            return send_file(return_data, mimetype='image/jpg',
                             download_name=filename, as_attachment=True)

    return render_template("compressImageLossless.html")


@app.route('/compressImageLossy', methods=['GET', 'POST'])
def imageCompressLossy():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            name = filename.split(".")[0]
            img = Image.open("uploads/"+filename)
            img = ImageOps.exif_transpose(img)
            img = img.resize(img.size, Image.ANTIALIAS)
            img = img.convert("RGB")
            img.save("uploads/"+name+".jpg", optimize=True, quality=10)
            return_data = io.BytesIO()
            with open("uploads/"+filename, 'rb') as fo:
                return_data.write(fo.read())
                return_data.seek(0)

            os.remove("uploads/"+filename)

            return send_file(return_data, mimetype='image/jpg',
                             download_name=filename, as_attachment=True)
    return render_template("compressImageLossy.html")


@app.route('/JPGtoPNG', methods=['GET', 'POST'])
def JPGtoPNG():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            name = filename.split(".")[0]
            img = Image.open("uploads/"+filename)
            img = ImageOps.exif_transpose(img)
            img = img.resize(img.size, Image.ANTIALIAS)
            img.save("uploads/"+name+".jpg", optimize=True, quality=50)
            img = Image.open("uploads/"+filename)
            img.save("uploads/"+name+".png", optimize=True)
            return_data = io.BytesIO()
            with open("uploads/"+filename, 'rb') as fo:
                return_data.write(fo.read())
                return_data.seek(0)

            os.remove("uploads/"+filename)

            return send_file(return_data, mimetype='image/png',
                             download_name=filename, as_attachment=True)
    return render_template("JPGtoPNG.html")


@app.route('/PNGtoJPG', methods=['GET', 'POST'])
def PNGtoJPG():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            name = filename.split(".")[0]
            img = Image.open("uploads/"+filename)
            img = img.convert("RGB")
            img.save("uploads/"+name+".jpg", optimize=True)
            return_data = io.BytesIO()
            with open("uploads/"+filename, 'rb') as fo:
                return_data.write(fo.read())
                return_data.seek(0)

            os.remove("uploads/"+filename)

            return send_file(return_data, mimetype='image/jpg',
                             download_name=filename, as_attachment=True)
    return render_template("PNGtoJPG.html")


#   PDF ilovepdf APIs
@app.route('/compressPDF', methods=['POST', 'GET'])
def compressPDF():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            name = filename.split(".")[0]

            # public key
            public_key = 'project_public_4318bad68fe4309f662794df25353a54_QGxwQ33b80c9b2aefdf2f9f2eb7cad021dfb0'

            # creating a ILovePdf object
            ilovepdf = ILovePdf(public_key, verify_ssl=True)

            # assigning a new compress task
            task = ilovepdf.new_task('compress')

            # adding the pdf file to the task
            task.add_file("./uploads/"+filename)

            # setting the output folder directory
            # if no folder exist it will create one
            task.set_output_folder('uploads')

            # execute the task
            task.execute()

            # download the task
            getname = task.download()

            # delete the task
            task.delete_current_task()
            return_data = io.BytesIO()
            with open("uploads/"+getname, 'rb') as fo:
                return_data.write(fo.read())
                return_data.seek(0)

            try:
                os.remove("uploads/"+filename)
                os.remove("uploads/"+getname)
            except:
                print("Removing issue")

            return send_file(return_data, mimetype='image/jpg',
                             download_name=filename, as_attachment=True)
    return render_template("compressPDF.html")


@app.route('/JPGtoPDF', methods=['POST', 'GET'])
def JPGtoPDF():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # name=filename.split(".")[0]

            # public key
            public_key = 'project_public_4318bad68fe4309f662794df25353a54_QGxwQ33b80c9b2aefdf2f9f2eb7cad021dfb0'

            # creating a ILovePdf object
            ilovepdf = ILovePdf(public_key, verify_ssl=True)

            # assigning a new compress task
            task = ilovepdf.new_task('imagepdf')

            # adding the pdf file to the task
            task.add_file("./uploads/"+filename)

            # setting the output folder directory
            # if no folder exist it will create one
            task.set_output_folder('uploads')

            # execute the task
            task.execute()

            # download the task
            getname = task.download()

            # delete the task
            task.delete_current_task()
            return_data = io.BytesIO()
            with open("uploads/"+getname, 'rb') as fo:
                return_data.write(fo.read())
                return_data.seek(0)

            try:
                os.remove("uploads/"+filename)
                os.remove("uploads/"+getname)
            except:
                print("Removing issue")

            return send_file(return_data, mimetype='image/jpg',
                             download_name=filename, as_attachment=True)
    return render_template("JPGtoPDF.html")


@app.route('/wordtoPDF', methods=['POST', 'GET'])
def wordtoPDF():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # name=filename.split(".")[0]

            # public key
            public_key = 'project_public_4318bad68fe4309f662794df25353a54_QGxwQ33b80c9b2aefdf2f9f2eb7cad021dfb0'

            # creating a ILovePdf object
            ilovepdf = ILovePdf(public_key, verify_ssl=True)

            # assigning a new compress task
            task = ilovepdf.new_task('officepdf')

            # adding the pdf file to the task
            task.add_file("./uploads/"+filename)

            # setting the output folder directory
            # if no folder exist it will create one
            task.set_output_folder('uploads')

            # execute the task
            task.execute()

            # download the task
            getname = task.download()

            # delete the task
            task.delete_current_task()
            return_data = io.BytesIO()
            with open("uploads/"+getname, 'rb') as fo:
                return_data.write(fo.read())
                return_data.seek(0)

            try:
                os.remove("uploads/"+filename)
                os.remove("uploads/"+getname)
            except:
                print("Removing issue")

            return send_file(return_data, mimetype='image/jpg',
                             download_name=filename, as_attachment=True)
    return render_template("wordtoPDF.html")


@app.route('/mergePDF', methods=['POST', 'GET'])
def mergePDF():
    if request.method == "POST":
        files = request.files.getlist("files")
        for file in files:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

        # public key
        public_key = 'project_public_4318bad68fe4309f662794df25353a54_QGxwQ33b80c9b2aefdf2f9f2eb7cad021dfb0'

        # creating a ILovePdf object
        ilovepdf = ILovePdf(public_key, verify_ssl=True)

        # assigning a new compress task
        task = ilovepdf.new_task('merge')
        for file in files:
            # adding the pdf file to the task
            task.add_file("./uploads/"+file.filename)

        # setting the output folder directory
        # if no folder exist it will create one
        task.set_output_folder('uploads')

        # execute the task
        task.execute()

        # download the task
        getname = task.download()

        # delete the task
        task.delete_current_task()
        return_data = io.BytesIO()
        with open("uploads/"+getname, 'rb') as fo:
            return_data.write(fo.read())
            return_data.seek(0)

        try:
            os.remove("uploads/"+filename)
            os.remove("uploads/"+getname)
        except:
            print("Removing issue")

        return send_file(return_data, mimetype='image/jpg',
                         download_name=filename, as_attachment=True)
    return render_template("mergePDF.html")


@app.route('/pagenumber', methods=['POST', 'GET'])
def pagenumber():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # name=filename.split(".")[0]

            # public key
            public_key = 'project_public_4318bad68fe4309f662794df25353a54_QGxwQ33b80c9b2aefdf2f9f2eb7cad021dfb0'

            # creating a ILovePdf object
            ilovepdf = ILovePdf(public_key, verify_ssl=True)

            # assigning a new compress task
            task = ilovepdf.new_task('pagenumber')

            # adding the pdf file to the task
            task.add_file("./uploads/"+filename)

            # setting the output folder directory
            # if no folder exist it will create one
            task.set_output_folder('uploads')

            # execute the task
            task.execute()

            # download the task
            getname = task.download()

            # delete the task
            task.delete_current_task()
            return_data = io.BytesIO()
            with open("uploads/"+getname, 'rb') as fo:
                return_data.write(fo.read())
                return_data.seek(0)

            try:
                os.remove("uploads/"+filename)
                os.remove("uploads/"+getname)
            except:
                print("Removing issue")

            return send_file(return_data, mimetype='image/jpg',
                             download_name=filename, as_attachment=True)
    return render_template("pagenumber.html")


if __name__ == "__main__":
    app.run(debug=True)
