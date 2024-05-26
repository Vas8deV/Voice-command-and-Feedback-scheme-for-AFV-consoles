# Voice-command-and-Feedback-scheme-for-AFV-consoles
This project develops a real-time speech recognition system for a vehicle console, utilizing OpenAI's Whisper model. The system converts spoken commands into text and provides spoken responses for user interaction.

Requirements:
- python 3.10.12
- Linux/Windows
- ffmpeg
- whisper (https://github.com/openai/whisper)
- faster-whisper (https://github.com/SYSTRAN/faster-whisper)
- torch 2.2.2
- sounddevice 0.4.6
- numpy 1.24.3
- scipy 1.8.0
- pyttsx3 2.90 (python-TTS text to speech library)

Flowchart:

![flowcdraft](https://github.com/Vas8deV/Voice-command-and-Feedback-scheme-for-AFV-consoles/assets/126313237/da8a7828-1584-4865-8ceb-0a7d0a332ca5)

Features of System:
1. The system remains active and listens for user commands once initiated. It
can only be stopped by the user through manual interruption.
2. The system prioritizes ongoing tasks like transcription or speech synthesis. It
will temporarily pause user input processing during these activities.
3.User interaction requires activating voice mode with specific keywords.
4.Only commands spoken while voice mode is active are recognized and
processed.
5. If a spoken command matches a defined action within the system, the system
translates it into corresponding control codes and communicates them to the vehicle
(assuming vehicle control functionality is implemented) and responds with feedback
through synthesized speech.
6. Voice mode can be deactivated by either user-spoken exit keywords or
automatically after a period of silence exceeding a set threshold.

Workflow of System:
1. Records audio in small chunks using the sounddevice library.
2. Analyse each chunk for speech activity based on volume and frequency.
3. If speech is detected, it adds the chunk to a buffer.
4. When enough silence is detected after speech or the buffer reaches a certain
size, it saves the buffered audio to a temporary WAV file.
5. The Whisper ASR model transcribes the audio file, producing a text transcript.
6. The transcribed text undergoes pre-processing and is then analyzed for the
presence of predefined keywords or phrases associated with specific commands.
7. If a recognized command is identified, the system executes the corresponding
action.
8. The system might provide feedback through synthesized speech or visual cues
to confirm command execution or prompt for further input. The loop then restarts,
continuously listening for and processing new speech commands.
9. The buffer is reset, and the process repeats, continuously listening for and
transcribing speech until the program is manually interrupted.

References:

[1] https://github.com/AI4Bharat/NPTEL2020- Indian-English-Speech-Dataset

[2] https://github.com/Nikorasu/LiveWhisper

Future Scope:
For working in a noisy environment other than using existing technologies like ANC (Active Noise Cancellation) or Directional microphones, we can implement the proposed neural network based denoising and speech enhancement methods.
