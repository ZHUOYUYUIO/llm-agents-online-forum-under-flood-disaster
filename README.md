# LLM-agents for online forum simulation under disaster Project

This is an intelligent agent generation system based on Flask and OpenAI.

## Project Structure

```
.
├── app.py                 # Main application file
├── persona_generator.py   # Persona generator
├── requirements.txt       # Project dependencies
├── .env                   # Environment variables
├── templates/            # HTML templates
└── static/              # Static resources
```

## Environment Requirements

- Python 3.7+
- pip

## Installation Steps

1. Clone the project to local
2. Create and activate virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Fill in necessary configuration information in `.env` file

## Running the Project

```bash
python app.py
```

## Main Features

- OpenAI-based persona generation
- Web interface interaction
- Real-time communication support

## LLM Agent Simulation Process

The system simulates intelligent agents through the following process:

1. **Persona Generation**: Creates detailed character profiles with specific traits, backgrounds, and behaviors
2. **Context Management**: Maintains conversation history and context awareness
3. **Response Generation**: Uses OpenAI's language model to generate contextually appropriate responses
4. **Real-time Interaction**: Enables seamless communication between users and agents
5. **State Management**: Tracks and updates agent states throughout conversations

## Dependencies

- Flask 2.0.1
- Flask-SocketIO 5.1.1
- OpenAI 0.27.0
- Other dependencies can be found in requirements.txt

## Notes

- Ensure proper configuration of OpenAI API key before use
- Recommended for development environment use # llm-agents-online-forum-under-flood-disaster
