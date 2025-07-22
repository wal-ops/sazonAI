from flask import Flask
import os
from src.controllers.recipe_controller import recipes_bp # Importar blueprint
from src.controllers.ingredient_controller import ingredients_bp # Importar blueprint
from config.database import init_app_db # Función para inicializar la conexión (la crearemos luego)

def create_app():
    app = Flask(__name__,
                  static_folder='static',
                  template_folder='templates')

    # Configuración de la clave secreta
    app.secret_key = os.getenv('SECRET_KEY', 'una-clave-secreta-por-defecto-para-desarrollo')

    # Registrar Blueprints
    app.register_blueprint(recipes_bp, url_prefix='/')
    app.register_blueprint(ingredients_bp, url_prefix='/')

    # Inicializar la conexión a la BD
    init_app_db(app)

    return app
