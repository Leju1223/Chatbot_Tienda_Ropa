from flask import Flask, request, jsonify

app = Flask(__name__)

# Diccionario global para mantener el estado de la conversación (sesión simplificada)
session_data = {}

# Productos disponibles
available_products = ["blusa", "jeans", "chaqueta"]

# Colores disponibles para los productos
available_colors = {
    "blusa": ["blanca", "negra", "roja", "azul", "verde"],
    "jeans": ["azul", "negro", "blanco"],
    "chaqueta": ["negra", "gris", "roja"]
}

# Tallas disponibles para los productos
available_sizes = {
    "blusa": ["S", "M", "L", "XL"],
    "jeans": ["S", "M", "L", "XL"],
    "chaqueta": ["S", "M", "L", "XL"]
}

# Respuestas básicas del chatbot
responses = {
    "donde se encuentran ubicados?": "Nuestra tienda es completamente virtual, operamos en Bogotá, pero no tenemos una ubicación física.",
    "que precio tienen las blusas?": "Los precios de las blusas varían dependiendo del estilo y la temporada. Puedes ver nuestras opciones en la página web.",
    "manejan prendas para hombre o para mujer?": "Tenemos prendas tanto para hombres como para mujeres. Puedes encontrar las colecciones en nuestra tienda en línea.",
    "que colores tienen disponibles?": "Ofrecemos varios colores, dependiendo de la prenda. Algunos de los más populares son blanco, negro, azul, rojo, y verde.",
    "tiene disponible jeans para dama?": "Sí, tenemos jeans para dama disponibles. Visita nuestra tienda en línea para ver las opciones y tallas disponibles."
}

# Función que genera la respuesta del chatbot y maneja la compra
def get_chatbot_response(user_message, user_session):
    # Convertir el mensaje a minúsculas para facilitar las comparaciones
    user_message = user_message.lower()

    # Verificar si el mensaje es una pregunta general
    if user_message in responses:
        return responses[user_message]

    # Si el usuario ha comenzado a comprar
    if 'comprar' in user_message or 'quiero comprar' in user_message:
        if user_session.get('producto'):
            return "¿Cuántos productos te gustaría comprar?"
        user_session['producto'] = None  # No hay producto seleccionado aún
        return "¿Te gustaría comprar una blusa, jeans o chaqueta? Responde con el nombre del producto que te interesa."

    # Si el usuario menciona un producto específico
    if user_session.get('producto') is None:
        if user_message in available_products:
            user_session['producto'] = user_message
            return f"Has elegido {user_message}. ¿Qué color prefieres? Los colores disponibles son: {', '.join(available_colors[user_message])}."
        else:
            return f"Lo siento, no tenemos {user_message} disponible. Por favor, elige entre blusa, jeans o chaqueta."

    # Si el usuario menciona un color
    if 'color' not in user_session:
        if user_message in available_colors[user_session['producto']]:
            user_session['color'] = user_message
            return f"Has elegido el color {user_message}. ¿Qué talla prefieres? Las tallas disponibles son: {', '.join(available_sizes[user_session['producto']])}."
        else:
            return f"Lo siento, no tenemos el color {user_message} para {user_session['producto']}. Por favor, elige entre los colores disponibles: {', '.join(available_colors[user_session['producto']])}."

    # Si el usuario menciona una talla
    if 'talla' not in user_session:
        if user_message.upper() in available_sizes[user_session['producto']]:
            user_session['talla'] = user_message.upper()
            return f"Has elegido la talla {user_message.upper()}. ¿Cuántos productos te gustaría comprar?"
        else:
            return f"Lo siento, no tenemos la talla {user_message} para {user_session['producto']}. Las tallas disponibles son: {', '.join(available_sizes[user_session['producto']])}."

    # Si el usuario proporciona una cantidad
    if user_message.isdigit():
        quantity = int(user_message)
        user_session['cantidad'] = quantity
        return f"Has seleccionado {quantity} {user_session['producto']} en color {user_session['color']} y talla {user_session['talla']}. ¿Cuál es tu dirección de envío?"

    # Si el usuario proporciona una dirección de envío
    if 'direccion' in user_session and not user_session.get('pago'):
        user_session['direccion'] = user_message
        return "Perfecto, ahora, ¿qué método de pago te gustaría usar? (Ejemplo: tarjeta de crédito, PayPal)"

    # Si el usuario proporciona un método de pago
    if 'direccion' in user_session and 'pago' not in user_session:
        user_session['pago'] = user_message
        return f"¡Gracias por tu compra! Hemos recibido tu pedido de {user_session['cantidad']} {user_session['producto']} en color {user_session['color']} y talla {user_session['talla']}, y será enviado a {user_session['direccion']}. El pago será realizado con {user_session['pago']}."

    # Respuesta predeterminada para preguntas que no están en el flujo de compra
    return "Lo siento, no entiendo la pregunta. ¿Puedes reformularla?"

# Ruta para el chatbot
@app.route('/chat', methods=['POST'])
def chat():
    # Obtener el mensaje del usuario desde la solicitud JSON
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({"error": "No se recibió mensaje"}), 400

    user_message = data.get('message')

    # Obtener el identificador de la sesión si existe
    user_session = session_data.get('session', {})

    # Obtener la respuesta del chatbot
    response_message = get_chatbot_response(user_message, user_session)

    # Actualizar la sesión
    session_data['session'] = user_session

    # Devolver la respuesta en formato JSON
    return jsonify({
        "response": response_message,
        "session": session_data.get('session', {})
    })

if __name__ == '__main__':
    app.run(debug=True)
