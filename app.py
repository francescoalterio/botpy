import discord
from discord.ext import commands
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime
from pytz import utc
import os
from dotenv import load_dotenv

load_dotenv()

firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
cred = credentials.Certificate(json.loads(firebase_credentials))  # Convertir el JSON a un diccionario
initialize_app(cred)
db = firestore.client() 

token = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def juegos(ctx):
    channel_name = ctx.channel.name
    if channel_name != "consultar-juegos":
        return

    try:
        await ctx.channel.purge(limit=100)

        juegos_ref = db.collection("juegos")
        docs = juegos_ref.stream()

        await ctx.send("**Lista completa de juegos registrados en la base de datos:**")

        juegos = []
        for doc in docs:
            juegos.append(doc.to_dict())  # Convertir cada documento a un diccionario

        if not juegos:
            await ctx.send("No hay juegos registrados en la base de datos.")
            return

        for juego in juegos:
            fecha = juego.get("fecha")
            if fecha and isinstance(fecha, datetime):
                fecha = fecha.strftime("%d/%m/%Y")  # Formatear a dd/mm/yyyy
            else:
                fecha = "N/A"
            mensaje = "**---------------------------------------**\n"
            mensaje += "**#########################**\n"
            mensaje += "**---------------------------------------**\n"
            mensaje += f"**Nombre del juego:** {juego.get('nombre', 'N/A')}\n"
            mensaje += f"**Fecha de salida:** {fecha}\n"
            mensaje += f"**Descripción:** {juego.get('descripcion', 'N/A')}\n"
            mensaje += f"**Trailer o video:** {juego.get('trailer', 'N/A')}\n"
            mensaje += f"{juego.get('poster', 'N/A')}\n"

            await ctx.send(mensaje)

    except Exception as e:
        print(f"Error al recuperar los juegos: {e}")
        await ctx.send("Ocurrió un error al intentar recuperar los juegos.")

@bot.command()
async def lanzamientos(ctx):
    channel_name = ctx.channel.name
    if channel_name != "consultar-juegos":
        return

    try:
        await ctx.channel.purge(limit=100)

        # Obtener la fecha actual con zona horaria UTC
        fecha_actual = datetime.now(utc)

        # Recuperar todos los documentos de la colección "juegos"
        juegos_ref = db.collection("juegos")
        docs = juegos_ref.stream()

        await ctx.send("**Juegos por salir**")

        juegos_futuros = []
        for doc in docs:
            juego = doc.to_dict()
            fecha = juego.get("fecha")
            if fecha and isinstance(fecha, datetime) and fecha > fecha_actual:
                juegos_futuros.append(juego)

        if not juegos_futuros:
            await ctx.send("No hay juegos próximos a lanzarse.")
            return

        # Mostrar los juegos futuros con el formato especificado
        for juego in juegos_futuros:
            fecha = juego["fecha"].strftime("%d/%m/%Y")
            mensaje = "**---------------------------------------**\n"
            mensaje += "**#########################**\n"
            mensaje += "**---------------------------------------**\n"
            mensaje += f"**Nombre del juego:** {juego.get('nombre', 'N/A')}\n"
            mensaje += f"**Fecha de salida:** {fecha}\n"
            mensaje += f"**Descripción:** {juego.get('descripcion', 'N/A')}\n"
            mensaje += f"**Trailer o video:** {juego.get('trailer', 'N/A')}\n"
            mensaje += f"{juego.get('poster', 'N/A')}\n"
            await ctx.send(mensaje)

    except Exception as e:
        print(f"Error al recuperar los lanzamientos: {e}")
        await ctx.send("Ocurrió un error al intentar recuperar los lanzamientos.")

@bot.command()
async def lanzados(ctx):
    channel_name = ctx.channel.name
    if channel_name != "consultar-juegos":
        return

    try:
        await ctx.channel.purge(limit=100)

        # Obtener la fecha actual con zona horaria UTC
        fecha_actual = datetime.now(utc)

        # Recuperar todos los documentos de la colección "juegos"
        juegos_ref = db.collection("juegos")
        docs = juegos_ref.stream()

        await ctx.send("**Juegos lanzados:**")


        juegos_pasados = []
        for doc in docs:
            juego = doc.to_dict()
            fecha = juego.get("fecha")
            if fecha and isinstance(fecha, datetime) and fecha <= fecha_actual:
                juegos_pasados.append(juego)

        if not juegos_pasados:
            await ctx.send("No hay juegos que ya hayan sido lanzados.")
            return

        # Mostrar los juegos pasados con el formato especificado
        for juego in juegos_pasados:
            fecha = juego["fecha"].strftime("%d/%m/%Y")
            mensaje = "**---------------------------------------**\n"
            mensaje += "**#########################**\n"
            mensaje += "**---------------------------------------**\n"
            mensaje += f"**Nombre del juego:** {juego.get('nombre', 'N/A')}\n"
            mensaje += f"**Fecha de salida:** {fecha}\n"
            mensaje += f"**Descripción:** {juego.get('descripcion', 'N/A')}\n"
            mensaje += f"**Trailer o video:** {juego.get('trailer', 'N/A')}\n"
            mensaje += f"{juego.get('poster', 'N/A')}\n"
            await ctx.send(mensaje)

    except Exception as e:
        print(f"Error al recuperar los lanzados: {e}")
        await ctx.send("Ocurrió un error al intentar recuperar los juegos lanzados.")

@bot.command()
async def ayuda(ctx):
    channel_name = ctx.channel.name
    if channel_name == "agregar-juegos":
        await ctx.send("""
        Comandos disponibles:
        !agregar - (Datos disponibles: nombre, descripcion, trailer, poster, fecha [Nota: colocar el nombre del dato, luego un espacio y el valor, luego un guion (-) y siguiente dato])
        !eliminar - (Elimina un juego de la base de datos, solo se necesita el nombre del juego [Sensible a mayúsculas y minúsculas])
        """)
    elif channel_name == "consultar-juegos":
        await ctx.send("""
        Comandos disponibles:
        !juegos - (Muestra todos los juegos registrados en la base de datos)
        !lanzamientos - (Muestra los juegos que aún no han salido)
        !lanzados - (Muestra los juegos que ya han salido)
        """)

@bot.command()
async def agregar(ctx, *, args):
    channel_name = ctx.channel.name
    if channel_name != "agregar-juegos":
        await ctx.send("Este comando solo se puede usar en el canal 'agregar-juegos'.")
        return

    # Dividir los argumentos por guiones
    partes = [parte.strip() for parte in args.split('-') if parte.strip()]
    datos = {}

    # Procesar cada par clave-valor
    for parte in partes:
        if " " in parte:
            clave, valor = parte.split(" ", 1)
            datos[clave.strip()] = valor.strip()

    # Procesar la fecha en formato dd/mm/yyyy
    fecha_str = datos.get("fecha", "")
    try:
        # Convertir la fecha proporcionada a un objeto datetime
        datos["fecha"] = datetime.strptime(fecha_str, "%d/%m/%Y") if fecha_str else None
    except ValueError:
        await ctx.send("El formato de la fecha debe ser 'dd/mm/yyyy'.")
        return

    # Validar que al menos el nombre esté presente
    if not datos.get("nombre"):
        await ctx.send("El nombre es obligatorio.")
        return

    try:
        # Guardar en Firestore
        doc_ref = db.collection("juegos").document(datos["nombre"])
        doc_ref.set(datos)
        await ctx.send(f"Juego '{datos['nombre']}' agregado con éxito.")
    except Exception as e:
        print(f"Error al guardar en Firestore: {e}")
        await ctx.send("Ocurrió un error al intentar guardar el juego en la base de datos.")

@bot.command()
async def eliminar(ctx, nombre):
    channel_name = ctx.channel.name
    if channel_name != "agregar-juegos":
        return

    try:
        doc_ref = db.collection("juegos").document(nombre)
        doc_ref.delete()
        await ctx.send(f"Juego '{nombre}' eliminado con éxito.")
    except Exception as e:
        print(f"Error al eliminar el juego: {e}")
        await ctx.send("Ocurrió un error al intentar eliminar el juego.")

bot.run(token)