import json
import base64
import requests
import os
from openai import OpenAI
from pydub import AudioSegment
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Retrieve the API key from the environment
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def text_to_speech(text, voice):
    completion = client.chat.completions.create(
        model="gpt-4o-audio-preview",
        modalities=["text", "audio"],
        audio={"voice": voice, "format": "mp3"},
        messages=[
            {
                "role": "system",
                "content": "You are a text-to-speech system for a fast-paced, energetic podcast. Convert the given text to audio verbatim, using appropriate emotional intonations for natural-sounding speech. The text is part of a larger podcast conversation. Your task is to convert the text to audio in an excited, upbeat podcast voice. Incorporate occasional laughter and other verbal sounds that naturally fit with podcast or radio shows. Do not embellish the text or add any additional words."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Please convert the following text to audio in a fast-paced, energetic podcast voice, exactly as it is.: {text}"
                    }
                ]
            },
        ]
    )
    
    audio_data = base64.b64decode(completion.choices[0].message.audio.data)
    return audio_data

def create_podcast(json_file):
    # Load conversation from JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    conversation = data['podcast']['conversation']
    
    # Create an empty audio segment
    podcast = AudioSegment.empty()
    
    # Process each line of the conversation
    for line in conversation[:4]:
        speaker = line['speaker']
        text = line['text']
        
        # Choose voice based on speaker
        voice = "shimmer" if speaker == "Alice" else "echo"
        
        # Convert text to speech
        audio_data = text_to_speech(text, voice)
        
        # Save temporary audio file
        temp_file = f"{speaker}_{voice}.mp3"
        with open(temp_file, "wb") as f:
            f.write(audio_data)
        
        # Load audio file and add to podcast
        segment = AudioSegment.from_mp3(temp_file)
        podcast += segment
        
        # Add a short pause between speakers
        podcast += AudioSegment.silent(duration=300)  # Reduced pause for faster pacing
    
    # Export the final podcast
    podcast.export("podcast_episode.mp3", format="mp3")

if __name__ == "__main__":
    create_podcast("convo.json")
