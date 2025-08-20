import io
from flask import Flask, request, send_file
from chatterbox.tts import ChatterboxTTS
import torchaudio as ta

# Load the TTS model
# Using "cpu" for portability, as we don't know if a GPU is available.
model = ChatterboxTTS.from_pretrained(device="cpu")

app = Flask(__name__)

@app.route('/tts', methods=['POST'])
def tts():
    """
    Text-to-speech endpoint.
    Takes 'text' and optional 'audio_prompt_path' in the request body.
    Returns a WAV file.
    """
    if not request.json or 'text' not in request.json:
        return "Please provide 'text' in the request body.", 400

    text = request.json['text']
    audio_prompt_path = request.json.get('audio_prompt_path')

    # Generate audio
    wav = model.generate(text, audio_prompt_path=audio_prompt_path)

    # Save to an in-memory buffer
    buffer = io.BytesIO()
    ta.save(buffer, wav, model.sr, format="wav")
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype='audio/wav',
        as_attachment=False,
        download_name='output.wav'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
