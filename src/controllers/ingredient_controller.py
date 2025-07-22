from flask import Blueprint, render_template, request, redirect, url_for
from config.database import get_db_connection
from src.controllers.recipe_controller import get_random_tip # Reutilizamos el generador de consejos

# Creamos el Blueprint para los ingredientes
ingredients_bp = Blueprint('ingredients', __name__)

# RUTA PARA LEER TODOS LOS INGREDIENTES (READ)
@ingredients_bp.route('/ingredients')
def list_ingredients():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, nombre, unidad_medida_predeterminada FROM ingredientes ORDER BY nombre;')
    ingredients_raw = cur.fetchall()
    cur.close()
    conn.close()

    ingredients = [{'id': i[0], 'nombre': i[1], 'unidad': i[2]} for i in ingredients_raw]
    
    return render_template('ingredient_list.html', ingredients=ingredients, consejo=get_random_tip())

# RUTAS PARA AÑADIR UN NUEVO INGREDIENTE (CREATE)
@ingredients_bp.route('/ingredient/add', methods=['GET', 'POST'])
def add_ingredient():
    if request.method == 'POST':
        nombre = request.form['nombre']
        unidad = request.form['unidad_medida']

        conn = get_db_connection()
        cur = conn.cursor()
        # El UNIQUE en la tabla 'ingredientes' previene duplicados
        try:
            cur.execute('INSERT INTO ingredientes (nombre, unidad_medida_predeterminada) VALUES (%s, %s);', (nombre, unidad))
            conn.commit()
        except Exception as e:
            conn.rollback() # Si hay un error (ej. nombre duplicado), deshacemos la transacción
            print(f"Error al insertar ingrediente: {e}")
        finally:
            cur.close()
            conn.close()
        
        return redirect(url_for('ingredients.list_ingredients'))

    # Para GET, solo muestra el formulario
    return render_template('ingredient_form.html', consejo=get_random_tip())

# RUTAS PARA EDITAR UN INGREDIENTE (UPDATE)
@ingredients_bp.route('/ingredient/edit/<int:id>', methods=['GET', 'POST'])
def edit_ingredient(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        unidad = request.form['unidad_medida']

        cur.execute(
            'UPDATE ingredientes SET nombre = %s, unidad_medida_predeterminada = %s WHERE id = %s;',
            (nombre, unidad, id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('ingredients.list_ingredients'))

    # Para GET, obtenemos los datos del ingrediente y los pasamos al formulario
    cur.execute('SELECT nombre, unidad_medida_predeterminada FROM ingredientes WHERE id = %s;', (id,))
    ingredient_raw = cur.fetchone()
    cur.close()
    conn.close()

    if ingredient_raw:
        ingredient = {'id': id, 'nombre': ingredient_raw[0], 'unidad': ingredient_raw[1]}
        return render_template('ingredient_form.html', ingredient=ingredient, consejo=get_random_tip())
    
    return redirect(url_for('ingredients.list_ingredients'))

# RUTA PARA BORRAR UN INGREDIENTE (DELETE)
@ingredients_bp.route('/ingredient/delete/<int:id>', methods=['POST'])
def delete_ingredient(id):
    conn = get_db_connection()
    cur = conn.cursor()
    # Usamos un try-except porque si un ingrediente está en uso, podría dar error de clave foránea
    try:
        cur.execute('DELETE FROM ingredientes WHERE id = %s;', (id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"No se puede borrar el ingrediente, probablemente está en uso en una receta. Error: {e}")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('ingredients.list_ingredients'))