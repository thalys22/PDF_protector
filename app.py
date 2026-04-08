from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
import os
import tempfile
import secrets
from pdf_modifier import modify_pdf

app = Flask(__name__)

# Load SECRET_KEY from environment for security; if missing, generate an ephemeral one
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
  # Ephemeral secret for local/dev only. Set SECRET_KEY in the environment for production.
  secret_key = secrets.token_hex(32)
app.config['SECRET_KEY'] = secret_key

# Use a writable temporary directory (serverless platforms like Vercel have a read-only filesystem)
tmp_upload_dir = os.path.join(tempfile.gettempdir(), 'pdf_protector_uploads')
os.makedirs(tmp_upload_dir, exist_ok=True)
app.config['UPLOAD_FOLDER'] = tmp_upload_dir

class CPFInputForm(FlaskForm):
  cpf = StringField('CPF', validators=[DataRequired()])
  position = SelectField('Position',
                         choices=[
                           ('top-left', 'Top Left'),
                           ('top-right', 'Top Right'),
                           ('bottom-left', 'Bottom Left'),
                           ('bottom-right', 'Bottom Right' )
                         ])
  Submit = SubmitField('Submit')
  color = StringField('Color', validators=[DataRequired()])
  
@app.route("/", methods=["GET", "POST"])
def upload_file():
  form = CPFInputForm()
  if form.validate_on_submit():
    if 'file' not in request.files:
      flash('Arquivo não icluido')
      return redirect(request.url)
    file = request.files['file']
    
    if file.filename == '':
      flash("Arquivo não selecionado")
      return redirect(request.url)
    
    if file:
      filename = secure_filename(file.filename)
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
      cpf = form.cpf.data
      position = form.position.data
      color = form.color.data
      
      try:
        modify_pdf(filename, cpf, position, color,
                   app.config["UPLOAD_FOLDER"])
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'],
                                      filename), as_attachment=True)
      except Exception as e:
        flash("Erro no envio do arquivo" + str(e))
        return redirect(request.url)
      
      
  return render_template('index.html', form=form)

