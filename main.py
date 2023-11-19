import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("recorder.html")

@app.route("/audio", methods=["POST"])
def audio():
    audio = request.files.get("audio")
    audio.save("audio.mp3")
    audio_file = open("audio.mp3", "rb")

    transcription = client.audio.transcriptions.create(model="whisper-1", file=audio_file)

    stream = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Eres un asistente malhablado"},
            {"role": "user", "content": transcription.text},
        ],
        model="gpt-3.5-turbo",
        stream=True
    )

    result = ""
    for part in stream:
        result += part.choices[0].delta.content or ""

    response = client.audio.speech.create(model="tts-1", voice="alloy", input=result)

    response.stream_to_file("static/output.mp3")                                                           
    
    return {"result": "ok", "text": result, "file": "output.mp3"}

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
