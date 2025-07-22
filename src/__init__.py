from flask import Flask
import os
# Asegúrate de que los blueprints se importen aquí
from .controllers.recipe_controller import recipes_bp
from .controllers.ingredient_controller import ingredients_bp
from config.database import init_app_db, close_db

def create_app():
    app = Flask(__name__,
                  static_folder='../static',  # Ajusta la ruta a static
                  template_folder='../templates') # Ajusta la ruta a templates

    # Configuración de variables de entorno
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    # Podrías añadir más configuraciones aquí si lo necesitas

    # Registrar Blueprints
    app.register_blueprint(recipes_bp)
    app.register_blueprint(ingredients_bp)

    # Inicializar y cerrar la conexión a la BD
    init_app_db(app)

    return app
