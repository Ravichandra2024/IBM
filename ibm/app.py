from flask import Flask, request, render_template
import io
import docx2txt
from pdfminer.high_level import extract_text
import requests

app = Flask(__name__)
api_key = '959a11faa87864ecfc512bf8d8d15b32'
translate_url = 'https://translate.googleapis.com/translate_a/single'

def summarize_text(text, api_key, sentences=3):
    url = 'https://api.meaningcloud.com/summarization-1.0'
    payload = {
        'key': api_key,
        'txt': text,
        'sentences': 3
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json()['summary']
    else:
        return f"Error {response.status_code}: {response.text}"

def translate_text(source_text, source_lang, target_lang):
    if source_lang == target_lang:
        return source_text
    
    params = {
        'client': 'gtx',
        'sl': source_lang,
        'tl': target_lang,
        'dt': 't',
        'q': source_text
    }
    response = requests.get(translate_url, params=params)
    if response.status_code == 200:
        data = response.json()
        translated_text = data[0][0][0]
        return translated_text
    else:
        return 'Translation error'
def ttranslate(source_text,source):
    source_lang = 'en'
    target_lang = source
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={source_lang}&tl={target_lang}&dt=t&q={source_text}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        result_text = data[0][0][0]
        return result_text
    else:
        return 'could not translate'
@app.route("/")
def index():
    return render_template("index.html", summary_text='Please upload a document (PDF, Word, or text)')

@app.route("/upload", methods=["POST"])
def upload():
    try:
        uploaded_file = request.files["file"]
        source_lang = request.form.get("language")
        target_lang = request.form.get("target_language")  

        if uploaded_file:
            file_content = uploaded_file.read()
            file_extension = uploaded_file.filename.split(".")[-1].lower()

            if file_extension == "pdf":
                text = extract_text(io.BytesIO(file_content))
            elif file_extension == "docx":
                text = docx2txt.process(io.BytesIO(file_content))
            else:
                text = file_content.decode('utf-8')
            if source_lang != 'en':
                translated_text = translate_text(text, source_lang, 'en')
            else:
                translated_text = text

            summarized_text = summarize_text(translated_text,api_key)
            summarized_text_translated = translate_text(summarized_text,"en",target_lang)
        

            return render_template("index.html", summary_text=summarized_text_translated)

    except Exception as e:
        return render_template("index.html", summary_text=str(e))

if __name__ == "__main__":
    app.run()