from flask import Flask, request, render_template
from openai import OpenAI
import os
from dotenv import load_dotenv
import yt_dlp
import re

load_dotenv()

app = Flask(__name__)
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def es_url_valida(url):
    return re.match(r'^https?://', url)

@app.route("/", methods=["GET", "POST"])
def index():
    resumen = ""
    error = ""
    if request.method == "POST":
        tipo = request.form["tipo"]
        contenido = request.form["contenido"].strip()

        if not contenido:
            error = "Por favor ingresá un contenido o URL válida."
        else:
            if tipo == "texto":
                resumen = resumir_texto(contenido)
            elif tipo == "noticia":
                resumen = resumir_url(contenido)
            elif tipo == "youtube":
                try:
                    resumen = resumir_video(contenido)
                except Exception as e:
                    error = f"Ocurrió un error al procesar el video: {str(e)}"
            elif tipo == "audio":
                resumen = resumir_audio(contenido)

    return render_template("index.html", resumen=resumen, error=error)

def resumir_texto(texto):
    respuesta = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Resumí este contenido de forma clara y concisa."},
            {"role": "user", "content": texto}
        ],
        temperature=0.5
    )
    return respuesta.choices[0].message.content.strip()

def resumir_url(url):
    import requests
    from bs4 import BeautifulSoup
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    texto = soup.get_text()
    return resumir_texto(texto[:5000])

def resumir_video(url):
    if not url or not es_url_valida(url):
        raise ValueError("La URL proporcionada no es válida.")

    with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        titulo = info.get('title', '')
        descripcion = info.get('description', '')
        return resumir_texto(f"Título: {titulo}\nDescripción: {descripcion}")

def resumir_audio(url):
    return "Funcionalidad en desarrollo (subí el audio en la versión futura)."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
