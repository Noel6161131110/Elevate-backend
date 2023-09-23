import json
from channels.generic.websocket import AsyncWebsocketConsumer
from queue import Queue
import pyaudio
import asyncio
from vosk import Model, KaldiRecognizer

class AudioConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages = Queue()
        self.recordings = Queue()
        self.CHANNELS = 1
        self.FRAME_RATE = 16000
        self.RECORD_SECONDS = 2
        self.AUDIO_FORMAT = pyaudio.paInt16
        self.model = Model(model_name="vosk-model-small-en-us-0.15")
        self.rec = KaldiRecognizer(self.model, self.FRAME_RATE)
        self.rec.SetWords(True)

    async def connect(self):
        print("Connected")
        await self.accept()

    async def disconnect(self, close_code):
        print("Disconnected")

    async def receive(self, bytes_data=None, text_data=None, bytes=False, **kwargs):
        # Handle incoming audio data here
        if bytes_data is not None:
        # Assuming `audio_data` is a binary audio data received from the client
            self.recordings.put(bytes_data)

            # You can perform speech recognition asynchronously
            asyncio.create_task(self.process_audio_data())

            # Send a confirmation message to the client
            await self.send(text_data=json.dumps({'message': 'Audio data received and being processed'}))
            
        else:
            print("No audio data received")

    async def process_audio_data(self):
        frames = self.recordings.get()
        self.rec.AcceptWaveform(b''.join(frames))
        result = self.rec.Result()
        text = json.loads(result)["text"]

        # Send the recognized text back to the client
        await self.send(text_data=json.dumps({'recognized_text': text}))

    def handle_recognized_text(self, text):
        # Implement your logic to handle the recognized text here
        # For example, you can save it to a file, process it further, etc.
        pass




