from flask import Flask, render_template, request
import json
import os
import requests as rq
import openai
from pathlib import Path
from base64 import b64decode
app = Flask(__name__)


path = r"C:\Users\corentin.fugier\Documents\Python Scripts\Dev_Web\site_2\static\images"
liste_gallerie = os.listdir(path)

def bored_api():
    dict = rq.get('http://www.boredapi.com/api/activity/')
    dict = dict.json()
    global bored_prompt
    bored_prompt = dict['activity']
    return bored_prompt

@app.route('/')
def index():
    return render_template('accueil.html')

@app.route('/gen')
def generator():
    return render_template('generator.html',bored_prompt = bored_api())

@app.route('/best-of')
def best():
    return render_template('best-of.html')

@app.route('/gallery')
def gallery():
    liste_path = []
    path = r"C:\Users\corentin.fugier\Documents\Python Scripts\Dev_Web\site_2\static\gallery"
    liste_gallerie = os.listdir(path)
    for name in liste_gallerie:
        liste_path.append("gallery/"+ name)
    return render_template('gallery.html', liste_path = liste_path)


def get_form():
    dict_request = {"user_message": str(request.form.get("user_message")),
            "background": str(request.form.get("background")),
             "art": str(request.form.get("art")),
             "job": str(request.form.get("job"))
             }
    prompt = dict_request['job']+' racoon '+ dict_request['user_message']+ ' '+' in '+dict_request['background']+', in'+dict_request['art']+' style'
    return {
        "prompt" : prompt,
        "art_type": dict_request['art'],
        

    }


@app.route('/gen', methods =["POST"])
def create_image():
    form = get_form()
    form = form["prompt"]
    prompt_gen = str(form)
    data_dir = Path.cwd() / "site_2"/ "responses"
    data_dir.mkdir(exist_ok=True)
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Image.create(
        prompt = prompt_gen,
        n=1,
        size="256x256",
        response_format="b64_json",
    )
    file_name = data_dir / f"{prompt_gen}-{response['created']}.json"

    with open(file_name, mode="w", encoding="utf-8") as file:
        json.dump(response, file)
    DATA_DIR = Path.cwd() / "site_2" / "responses"
    JSON_FILE = DATA_DIR / f"{prompt_gen}-{response['created']}.json"
    IMAGE_DIR = Path.cwd() / "site_2" / "static" / "gallery" 

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    with open(JSON_FILE, mode="r", encoding="utf-8") as file:
        response = json.load(file)

    for index, image_dict in enumerate(response["data"]):
        image_data = b64decode(image_dict["b64_json"])
        image_file = IMAGE_DIR / f"{JSON_FILE.stem}-{index}.png"
        with open(image_file, mode="wb") as png:
            image = png.write(image_data)
    return gallery()

app.run()