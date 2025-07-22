import random
from flask import Blueprint, render_template, request, redirect, url_for
from config.database import get_db_connection

# Creamos un "Blueprint", que es como un mini-app para organizar rutas.
recipes_bp = Blueprint("recipes", __name__)

# Lista de consejos del chef para mostrar en la página
chef_tips = [
    "Asegúrate de que tus cuchillos estén siempre afilados. Es más seguro y eficiente.",
    "Lee la receta completa antes de empezar a cocinar.",
    "Prueba tu comida mientras cocinas y ajusta la sazón.",
    "No sobrecargues la sartén; cocina en tandas para un dorado perfecto.",
    "Deja que la carne descanse unos minutos después de cocinarla antes de cortarla.",
]


def get_random_tip():
    return random.choice(chef_tips)


# RUTA PARA LEER TODAS LAS RECETAS (READ)
@recipes_bp.route('/dashboard')
def dashboard():
    conn = get_db() # Obtiene la conexión para esta petición
    if conn is None:
        flash('Error de conexión con la base de datos.', 'danger')
        return render_template('dashboard.html', recipes=[])

    try:
        cur = conn.cursor()
        # Tu lógica de consulta SQL...
        cur.execute("""
            SELECT r.id, r.nombre, r.descripcion, r.instrucciones, r.categoria,
                   STRING_AGG(i.nombre, ', ') AS ingredientes
            FROM recetas r
            LEFT JOIN receta_ingredientes ri ON r.id = ri.receta_id
            LEFT JOIN ingredientes i ON ri.ingrediente_id = i.id
            GROUP BY r.id
            ORDER BY r.nombre
        """)
        recipes = cur.fetchall()
        cur.close()
        return render_template('dashboard.html', recipes=recipes)
    except Exception as e:
        flash(f'Ocurrió un error al cargar las recetas: {e}', 'danger')
        return render_template('dashboard.html', recipes=[])


# RUTAS PARA AÑADIR UNA NUEVA RECETA (CREATE)
@recipes_bp.route("/recipe/add", methods=["GET", "POST"])
def add_recipe():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        # Obtenemos los datos del formulario
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        instrucciones = request.form["instrucciones"]
        id_usuario = request.form["id_usuario"]
        ingredient_ids = request.form.getlist(
            "ingredients"
        )  # IDs de los ingredientes seleccionados

        # Insertamos la nueva receta y obtenemos su ID
        cur.execute(
            "INSERT INTO recetas (nombre, descripcion, instrucciones, id_usuario) VALUES (%s, %s, %s, %s) RETURNING id;",
            (nombre, descripcion, instrucciones, id_usuario),
        )
        new_recipe_id = cur.fetchone()[0]

        # Asociamos los ingredientes a la nueva receta
        for ingredient_id in ingredient_ids:
            # Por simplicidad, la cantidad y unidad son fijas aquí. Se podría extender el formulario para incluirlas.
            cur.execute(
                "INSERT INTO recetas_ingredientes (id_receta, id_ingrediente, cantidad, unidad_medida) VALUES (%s, %s, %s, %s);",
                (new_recipe_id, int(ingredient_id), 1, "unidad"),
            )

        conn.commit()  # Guardamos todos los cambios en la base de datos
        cur.close()
        conn.close()
        return redirect(url_for("recipes.dashboard"))

    # Si es un GET, solo mostramos el formulario
    # Necesitamos obtener todos los ingredientes para mostrarlos como checkboxes
    cur.execute("SELECT id, nombre FROM ingredientes ORDER BY nombre;")
    all_ingredients_raw = cur.fetchall()
    all_ingredients = [{"id": i[0], "nombre": i[1]} for i in all_ingredients_raw]

    cur.close()
    conn.close()
    return render_template(
        "recipe_form.html", all_ingredients=all_ingredients, consejo=get_random_tip()
    )


# RUTAS PARA EDITAR UNA RECETA (UPDATE)
@recipes_bp.route("/recipe/edit/<int:id>", methods=["GET", "POST"])
def edit_recipe(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        instrucciones = request.form["instrucciones"]
        ingredient_ids = request.form.getlist("ingredients")

        # Actualizamos la tabla de recetas
        cur.execute(
            "UPDATE recetas SET nombre = %s, descripcion = %s, instrucciones = %s WHERE id = %s;",
            (nombre, descripcion, instrucciones, id),
        )

        # Actualizamos los ingredientes (la forma más fácil es borrar los antiguos e insertar los nuevos)
        cur.execute("DELETE FROM recetas_ingredientes WHERE id_receta = %s;", (id,))
        for ingredient_id in ingredient_ids:
            cur.execute(
                "INSERT INTO recetas_ingredientes (id_receta, id_ingrediente, cantidad, unidad_medida) VALUES (%s, %s, %s, %s);",
                (id, int(ingredient_id), 1, "unidad"),
            )

        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("recipes.dashboard"))

    # Para GET, cargamos los datos de la receta y sus ingredientes actuales
    cur.execute(
        "SELECT nombre, descripcion, instrucciones FROM recetas WHERE id = %s;", (id,)
    )
    recipe_raw = cur.fetchone()
    recipe = {
        "nombre": recipe_raw[0],
        "descripcion": recipe_raw[1],
        "instrucciones": recipe_raw[2],
    }

    cur.execute(
        "SELECT id_ingrediente FROM recetas_ingredientes WHERE id_receta = %s;", (id,)
    )
    recipe["ingredient_ids"] = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT id, nombre FROM ingredientes ORDER BY nombre;")
    all_ingredients_raw = cur.fetchall()
    all_ingredients = [{"id": i[0], "nombre": i[1]} for i in all_ingredients_raw]

    cur.close()
    conn.close()

    return render_template(
        "recipe_form.html",
        recipe=recipe,
        all_ingredients=all_ingredients,
        consejo=get_random_tip(),
    )


# RUTA PARA BORRAR UNA RECETA (DELETE)
@recipes_bp.route("/recipe/delete/<int:id>", methods=["POST"])
def delete_recipe(id):
    conn = get_db_connection()
    cur = conn.cursor()
    # Gracias al 'ON DELETE CASCADE' en la BD, al borrar la receta,
    # también se borrarán sus entradas en 'recetas_ingredientes'.
    cur.execute("DELETE FROM recetas WHERE id = %s;", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("recipes.dashboard"))


# RUTA PARA VER UNA SOLA RECETA (READ ONE)
@recipes_bp.route("/recipe/<int:id>")
def view_recipe(id):
    conn = get_db_connection()
    cur = conn.cursor()

    # Consulta para obtener los detalles de la receta y el nombre del autor
    cur.execute(
        """
        SELECT r.nombre, r.descripcion, r.instrucciones, u.nombre as autor
        FROM recetas r
        LEFT JOIN usuarios u ON r.id_usuario = u.id
        WHERE r.id = %s;
    """,
        (id,),
    )
    recipe_raw = cur.fetchone()

    if not recipe_raw:
        cur.close()
        conn.close()
        return "Receta no encontrada", 404

    # Consulta para obtener los ingredientes de esa receta
    cur.execute(
        """
        SELECT i.nombre, ri.cantidad, ri.unidad_medida
        FROM recetas_ingredientes ri
        JOIN ingredientes i ON ri.id_ingrediente = i.id
        WHERE ri.id_receta = %s;
    """,
        (id,),
    )
    ingredients_raw = cur.fetchall()

    cur.close()
    conn.close()

    recipe = {
        "nombre": recipe_raw[0],
        "descripcion": recipe_raw[1],
        "instrucciones": recipe_raw[2],
        "autor": recipe_raw[3],
    }
    ingredients = [
        {"nombre": i[0], "cantidad": i[1], "unidad": i[2]} for i in ingredients_raw
    ]

    return render_template(
        "recipe_detail.html",
        recipe=recipe,
        ingredients=ingredients,
        consejo=get_random_tip(),
    )
