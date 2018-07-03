import os
from datetime import datetime
from dateutil import parser as datetime_parser
from dateutil.tz import tzutc
from flask import Flask, url_for, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from utils import split_url


basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, '../data.sqlite')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

db = SQLAlchemy(app)

class ValidationError(ValueError):
    pass


class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), index=True)
    direccion = db.Column(db.String(120), index=True)
    telefono = db.Column(db.Integer, index=True)
    prestamos = db.relationship('Prestamo', backref='usuario', lazy='dynamic') #<---- relationship 

    def get_url(self):
        """
        Retonar el url del usuario, representado en formato json
        """
        return url_for('get_usuario', id=self.id, _external=True)


    def export_data(self):
        """
        genera información representado en formato json, del objeto usuario
        """


        return {
            'self_url': self.get_url(),
            'nombre': self.nombre,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'prestamos_url': url_for('get_prestamo_usuario', id=self.id, _external=True)
        }

    def import_data(self, data):
        """
        crea el nuevo recurso usuario, representado en formato json
        """
        try:
            self.nombre = data['nombre']
            self.direccion = data['direccion']
            self.telefono = data['telefono']
        except KeyError as e:
            raise ValidationError('Usuario no valido: ausente ...... ' + e.args[0])
        return self

class Prestamo(db.Model):
    __tablename__ = 'prestamos'
    id = db.Column(db.Integer, primary_key=True)
    fechaPrestamo = db.Column(db.String(64), index=True)
    fechaDevolucion = db.Column(db.String(64), index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    libro_id = db.Column(db.Integer, db.ForeignKey('libros.id'))

    def get_url(self):
        return url_for('get_prestamos', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'fechaPrestamo': self.fechaPrestamo,
            'fechaDevolucion': self.fechaDevolucion,
            'usuario_url': self.usuario.get_url(),
            'libro_url': self.libro.get_url()
            }

    def import_data(self, data):
        try:
            self.fechaPrestamo = data['fechaPrestamo']
            self.fechaDevolucion = data['fechaDevolucion']
        except KeyError as e:
            raise ValidationError('Prestamo no valido: prestamo' + e.args[0])
        return self

class Libro(db.Model):
    __tablename__ = 'libros'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(120), index=True)
    isbn = db.Column(db.String(11), index=True)
    editorial = db.Column(db.String(64), index=True)
    prestamos = db.relationship('Prestamo', backref='libro', lazy='dynamic', cascade='all, delete-orphan')
    autores = db.relationship('Autor', backref='libro', lazy='dynamic', cascade='all, delete-orphan')

    def get_url(self):
        return url_for('get_prestamo_libro', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'titulo': self.titulo,
            'isbn': self.isbn,
            'editorial': self.editorial,
            'prestamo_url': url_for('get_prestamo_libro', id=self.id, _external=True),
            'autor_url': url_for('get_autores_libro', id=self.id, _external=True)
        }

    def import_data(self, data):
        try:
            self.titulo = data['titulo']
            self.isbn = data['isbn']
            self.editorial = data['editorial']
        except KeyError as e:
            raise ValidationError('Libro no valido: perdido' + e.args[0])
        return self

class Autor(db.Model):
    __tablename__ = 'autores'
    id = db.Column(db.Integer, primary_key=True)
    libro_id = db.Column(db.Integer, db.ForeignKey('libros.id'), index=True)
    name = db.Column(db.String(64), index=True)
    nacionalidad = db.Column(db.String(64), index=True)

    def get_url(self):
        return url_for('get_autores', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'libro_url': self.libro.get_url(),
            'name': self.name,
            'nacionalidad': self.nacionalidad
        }

    def import_data(self, data):
        try:
            self.name = data['name']
            self.nacionalidad = data['nacionalidad']
        except KeyError as e:
            raise ValidationError('Autor no valido: perdido' + e.args[0])
        return self

# modulos de rutas
# ----USUARIOS

@app.route('/usuarios/', methods=['GET'])
def get_usuarios():
    """
    Función que obtiene la lista de usuarios, con contenido obtenido por listas por comprensión
    """
    #print('-------------')
    #for usuario in Cliente.query.all():
    #    print(cliente.get_url())
    #print('-------------')

    return jsonify({'usuarios': [usuario.get_url() for usuario in
                                 Usuario.query.all()]})

@app.route('/usuarios/', methods=['POST'])
def new_usuario():
    """
    Función que crea un usuario
    """
    usuario = Usuario()
    print(".....request.json......")
    print(request.json)
    print(request)
    print(".....request.json......")
    
    usuario.import_data(request.json)
    db.session.add(usuario)
    db.session.commit()
    return jsonify({}), 201, {'Localizacion': usuario.get_url()}

@app.route('/usuarios/<int:id>', methods=['GET'])
def get_usuario(id):
    """
    Lista individualmente a los clientes
    print("solo conslta %s" % Cliente.query.get_or_404(id).export_data())
    print("en formato json: ")
    print (jsonify(Cliente.query.get_or_404(id).export_data()))
    """ 
    return jsonify(Usuario.query.get_or_404(id).export_data())

# ----- PRESTAMOS
@app.route('/prestamos/', methods=['GET'])
def get_prestamos():
    print("entro aqui!!!")
    return jsonify({'prestamos': [prestamo.get_url() for prestamo in Prestamo.query.all()]})

@app.route('/prestamos/<int:id>', methods=['GET'])
def get_prestamo(id):
    return jsonify(Prestamo.query.get_or_404(id).export_data())

@app.route('/usuarios/<int:id>/prestamos/', methods=['GET'])
def get_prestamo_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    return jsonify({'usuarios': [prestamo.get_url() for prestamo in usuario.prestamos.all()]})

@app.route('/usuarios/<int:id>/prestamos/', methods=['POST'])
def nuevo_prestamo_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    prestamo = Prestamo(usuario=usuario)
    prestamo.import_data(request.json)
    db.session.add(prestamo)
    db.session.commit()
    return jsonify({}), 201, {'Localización': prestamo.get_url()}

@app.route('/libros/<int:id>/prestamos/', methods=['GET'])
def get_prestamo_libro(id):
    libro = Libro.query.get_or_404(id)
    return jsonify({'libros': [prestamo.get_url() for prestamo in libro.prestamos.all()]})

@app.route('/libros/<int:id>/prestamos/', methods=['POST'])
def nuevo_prestamo_libro(id):
    libro = Libro.query.get_or_404(id)
    prestamo = Prestamo(libro=libro)
    prestamo.import_data(request.json)
    db.session.add(prestamo)
    db.session.commit()
    return jsonify({}), 201, {'Localización': prestamo.get_url()}

@app.route('/prestamos/<int:id>', methods=['PUT'])
def edit_prestamos(id):
    prestamo = Prestamo.query.get_or_404(id)
    prestamo.import_data(request.json)
    db.session.add(prestamo)
    db.session.commit()
    return jsonify({})

@app.route('/prestamos/<int:id>', methods=['DELETE'])
def delete_prestamo(id):
    prestamo = Prestamo.query.get_or_404(id)
    db.session.delete(prestamo)
    db.session.commit()
    return jsonify({})

#---- LIBROS
@app.route('/libros/', methods=['GET'])
def get_libros():
    return jsonify({'libros': [libro.get_url() for libro in Libro.query.all()]})

@app.route('/libros/', methods=['POST'])
def nuevo_libro():
    libro = Libro()
    libro.import_data(request.json)
    db.session.add(libro)
    db.session.commit()
    return jsonify({}), 201, {'Localizacion': libro.get_url()}

@app.route('/libros/<int:id>', methods=['PUT'])
def edit_libros(id):
    libro = Libro.query.get_or_404(id)
    libro.import_data(request.json)
    db.session.add(libro)
    db.session.commit()
    return jsonify({})

@app.route('/libros/<int:id>', methods=['DELETE'])
def delete_libro(id):
    libro = Libro.query.get_or_404(id)
    db.session.delete(libro)
    db.session.commit()
    return jsonify({})

# ----- AUTORES
@app.route('/autores/', methods=['GET'])
def get_autores():
    print("entro aqui!!!")
    return jsonify({'autores': [autor.get_url() for autor in Autor.query.all()]})

@app.route('/libros/<int:id>/autores/', methods=['GET'])
def get_autores_libro(id):
    libro = Libro.query.get_or_404(id)
    return jsonify({'libros': [autor.get_url() for autor in libro.autores.all()]})

@app.route('/libros/<int:id>/autores/', methods=['POST'])
def nuevo_autor_libro(id):
    libro = Libro.query.get_or_404(id)
    autor = Autor(libro=libro)
    autor.import_data(request.json)
    db.session.add(autor)
    db.session.commit()
    return jsonify({}), 201, {'Localización': autor.get_url()}

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
