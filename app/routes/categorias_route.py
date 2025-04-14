import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required,current_user
from werkzeug.utils import secure_filename
from app.models.categorias import Categorias
from app import db
import uuid 

bp = Blueprint('categorias', __name__)


# hacer que todas las rutas necesiten el logeo
@bp.before_request
@login_required
def before_request():
    pass

# Configuración para la subida de imágenes
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','jfif','webp','bmp','ico'}
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'imagenes')  # Ruta absoluta

# Verificar que la carpeta existe, si no, crearla
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Verifica si la extensión del archivo es válida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def subir_imagen(img, img_actual=None):
    """Guarda una imagen con un nombre aleatorio y elimina la anterior si existe."""

    if img and allowed_file(img.filename):
        try:
            # Obtener extensión del archivo
            ext = img.filename.rsplit('.', 1)[1].lower()
            # Generar nombre único aleatorio
            nuevo_nombre = f"{uuid.uuid4().hex}.{ext}"
            # Ruta completa donde se guardará
            filepath = os.path.join(UPLOAD_FOLDER, nuevo_nombre)

            # Guardar imagen nueva
            img.save(filepath)
            print(f"✅ Imagen guardada: {filepath}")

            # Eliminar la imagen anterior si no es la predeterminada
            if img_actual and img_actual != "categoria.png":
                path_anterior = os.path.join(UPLOAD_FOLDER, img_actual)
                if os.path.exists(path_anterior):
                    os.remove(path_anterior)
                    print(f"🗑 Imagen anterior eliminada: {path_anterior}")

            return nuevo_nombre  # Devuelve el nuevo nombre

        except Exception as e:
            flash(f"❌ Error al guardar la imagen: {str(e)}", "error")
            print(f"❌ Error al guardar la imagen: {str(e)}")

    # Si no se subió nueva imagen o hubo error, mantener la anterior
    return img_actual or "categoria.png"

@bp.route('/categorias')
def index():
    data = Categorias.query.all()
    return render_template('categorias/index.html', data=data,datausu=current_user)

@bp.route('/carrusel')
def carrusel():
    data = Categorias.query.all()
    return render_template('categorias/carrusel.html', data=data)

@bp.route('/categorias/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':

        nombre = request.form['nombre']
        new_cat = Categorias(nombre=nombre)
        # Subir imagen si está en la solicitud
        img1 = subir_imagen(request.files.get('img1'))
        new_cat.img1= img1
        db.session.add(new_cat)
        try:
            db.session.commit()
            flash('✅ Categoria creada correctamente')
        except:
            print("Error en la base de datos add categorias")
        return redirect(url_for('categorias.index'))
    
    return render_template('categorias/add.html')

@bp.route('/categorias/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    categoria = Categorias.query.get_or_404(id)

    if request.method == 'POST':
        categoria.nombre = request.form['nombre']
        # Subir la nueva imagen y eliminar la anterior
        if 'img1' in request.files and request.files['img1'].filename:
            categoria.img1 = subir_imagen(request.files['img1'], categoria.img1)
        try:
            db.session.commit()
            flash('✅ Categoria Actualizada correctamente') 
        except:
            print("Error en la base de datos edit categorias")     
        return redirect(url_for('categorias.index'))

    return render_template('categorias/edit.html', datacat=categoria)

@bp.route('/categorias/delete/<int:id>')
def delete(id):
    categoria = Categorias.query.get_or_404(id)
    try:
           # Eliminar imágenes si existen (opcional)
        if categoria.img1 and categoria.img1 != "categoria.png":
            ruta_img = os.path.join(UPLOAD_FOLDER, 'static', 'imagenes', categoria.img1)
        if os.path.exists(ruta_img):
            os.remove(ruta_img)
        db.session.delete(categoria)
        db.session.commit()
        flash("✅ Categoria eliminada con éxito", "success")
    except:
        flash("Error en la base de datos Eliminar Categoria")
    return redirect(url_for('categorias.index'))

@bp.route('/categorias/filtro/<int:id>')
def productos_por_categoria(id):
    # Lógica para mostrar productos de la categoría con el id proporcionado
    pass



