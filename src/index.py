from flask import Flask, redirect, url_for
from src.controllers.recipe_controller import recipes_bp

# 1. Importa el nuevo blueprint
from src.controllers.ingredient_controller import ingredients_bp
app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.register_blueprint(recipes_bp)

# 2. Registra el blueprint de ingredientes
app.register_blueprint(ingredients_bp)
@app.route('/')
def index():
    return redirect(url_for('recipes.dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)