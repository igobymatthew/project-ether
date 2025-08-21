# Project Ether

An experimental audio-LLM playground for simulating lively group calls.

## Capabilities

Project Ether simulates a group call with fictional characters.

-   **Expressive, natural voices**: Characters speak with natural-sounding voices.
-   **Real-time conversation**: Interact with characters in real-time.
-   **Background audio**: Includes background sounds for a more immersive experience.
-   **Dynamic conversations**: The conversation can shift between different speakers.

## How to Run

This project consists of three main components: a **main API backend**, a **Text-to-Speech (TTS) service**, and a **frontend**. Due to conflicting Python dependencies between the two backend services, they must be run in separate environments.

### 1. Generate Character Agents

First, generate the agent configuration files needed for the simulation:
```bash
python scripts/make_agents.py
```

### 2. Run the Backend Services

You will need two separate terminals for the backend services.

**Terminal 1: Main API**

1.  **Set up the environment:**
    ```bash
    python -m venv .venv-main
    source .venv-main/bin/activate   # On Windows: .venv-main\Scripts\activate
    pip install -r app/api/main/requirements.txt
    ```

2.  **Run the server:**
    ```bash
    uvicorn app.api.main.main:app --reload --port 8000
    ```
    This service handles the main application logic and orchestration. You can check if it's running by visiting `http://localhost:8000/`.

**Terminal 2: TTS Service**

1.  **Set up the environment:**
    ```bash
    python -m venv .venv-tts
    source .venv-tts/bin/activate   # On Windows: .venv-tts\Scripts\activate
    pip install -r app/api/tts/requirements.txt
    ```
    *Note: The TTS dependencies include large PyTorch models. The first installation may take some time.*

2.  **Run the server:**
    ```bash
    uvicorn app.api.tts.main:app --reload --port 8001
    ```
    This service is dedicated to generating audio from text. You can check if it's running by visiting `http://localhost:8001/`.

### 3. Run the Frontend

Finally, open a third terminal to serve the frontend application.

1.  **Run the server:**
    ```bash
    python -m http.server --directory app/frontend 8080
    ```

2.  **Open the application:**
    Open your browser and navigate to `http://localhost:8080/index.html`.

## Usage

-   **Start Call**: Click the "Dial" button to connect and start the simulation.
-   **Interact**: Type a message in the input box to have a character respond.
-   **Switch Speakers**: Try asking to speak to a different character, for example, "Can I talk to my brother?".
-   **Adjust Volume**: Use the slider to change the volume of the background audio.
-   **End Call**: Click the "End Call" button to stop the simulation.
