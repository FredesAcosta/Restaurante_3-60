# utils.py
import os
from pymysql import IntegrityError, DataError, OperationalError, ProgrammingError, DatabaseError
from twilio.rest import Client

# =====================================================
# MANEJADOR DE ERRORES DE BASE DE DATOS
# =====================================================
def manejar_error_db(e, conn=None):
    """
    Maneja los diferentes tipos de errores de base de datos y devuelve un mensaje adecuado.
    """
    import logging
    logger = logging.getLogger(__name__)

    # Verificar si conn es una conexión válida
    if conn and hasattr(conn, 'rollback'):
        try:
            conn.rollback()
        except Exception as rollback_e:
            logger.error(f"Error al hacer rollback: {rollback_e}")
    elif conn:
        logger.warning(f"Objeto conn no válido para rollback: {type(conn)}")

    if isinstance(e, IntegrityError):
        mensaje = "Error: el dato ya existe o viola una restricción única."
    elif isinstance(e, DataError):
        mensaje = "Error: formato o tipo de dato incorrecto."
    elif isinstance(e, ProgrammingError):
        mensaje = "Error interno en la consulta SQL."
    elif isinstance(e, OperationalError):
        mensaje = "Error de conexión o permisos en la base de datos."
    elif isinstance(e, DatabaseError):
        mensaje = "Error general de base de datos."
    else:
        mensaje = f"Error inesperado: {str(e)}"

    logger.error(f"[LOG DE ERROR] {type(e).__name__}: {e}")
    return mensaje


# =====================================================
# ENVÍO DE SMS CON TWILIO
# =====================================================

# Cargar configuración desde variables de entorno
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def enviar_codigo_sms(numero, codigo):
    """
    Envía un SMS con el código de recuperación al número indicado.
    Devuelve True si fue exitoso, False si hubo error.
    """
    try:
        # Aseguramos formato E.164 (+57...)
        if not numero.startswith("+57"):
            numero = f"+57{numero}"

        # Validar que el número tenga al menos 10 dígitos después de +57
        numero_sin_prefijo = numero.replace("+57", "")
        if len(numero_sin_prefijo) < 10:
            print(f"[ERROR TWILIO] Número inválido: {numero} (muy corto)")
            return False

        message = client.messages.create(
            body=f"Tu código de recuperación es: {codigo}",
            from_=TWILIO_PHONE_NUMBER,
            to=numero
        )
        print(f"[OK] Código {codigo} enviado a {numero}, SID: {message.sid}")
        return True
    except Exception as e:
        print(f"[ERROR TWILIO] {type(e).__name__}: {e}")
        return False
