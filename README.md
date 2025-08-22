# Project Ether

An experimental audio-LLM playground for simulating lively group calls.

## Capabilities

Project Ether simulates a group call with fictional characters.

-   **Expressive, natural voices**: Characters speak with natural-sounding voices.
-   **Real-time conversation**: Interact with characters in real-time.
-   **Background audio**: Includes background sounds for a more immersive experience.
-   **Dynamic conversations**: The conversation can shift between different speakers.

## How to Run

This project uses a "vendored" dependency approach to manage conflicting dependencies between the main API and the TTS service. This allows the services to run on the same machine without requiring virtual environments or Docker.

### 1. Install Dependencies

First, create the vendor directories to hold the isolated dependencies for each service:
```bash
mkdir -p vendor/api_site vendor/tts_site
```

Next, install the dependencies for each service into its respective directory:

**API Dependencies:**
```bash
python -m pip install --target vendor/api_site -r requirements-api.txt
```

**TTS Dependencies:**
```bash
python -m pip install --target vendor/tts_site -r requirements-tts.txt
```

### 2. Run the Services

You will need two separate terminals to run the backend services. The provided launcher scripts in the `ops/` directory will automatically manage the Python path to ensure each service uses its correct set of dependencies.

**Terminal 1: Main API**
```bash
python ops/run_api.py
```
This service handles the main application logic and orchestration. It will be available at `http://localhost:8000`.

**Terminal 2: TTS Service**
```bash
python ops/run_tts.py
```
This service is dedicated to generating audio from text. It will be available at `http://localhost:8010`.

### 3. Run the Frontend

Finally, open a third terminal to serve the frontend application:
```bash
python -m http.server --directory app/frontend 8080
```

### 4. Access the Application

Open your browser and navigate to `http://localhost:8080/index.html`.

## Usage

-   **Start Call**: Click the "Dial" button to connect and start the simulation.
-   **Interact**: Type a message in the input box to have a character respond.
-   **Switch Speakers**: Try asking to speak to a different character (e.g., "Can I talk to my brother?").
-   **Adjust Volume**: Use the slider to change the volume of the background audio.
-   **End Call**: Click the "End Call" button to stop the simulation.

## Development

This project is configured as a Python package using `pyproject.toml`. If you add new modules or top-level directories like `app` or `services`, update the `[tool.setuptools.packages.find]` section in `pyproject.toml`.

To check for import errors after making changes, you can run the provided smoke test script:
```bash
python tools/import_smoke.py
```
