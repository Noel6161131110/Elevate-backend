from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import string, os, json
from pydub import AudioSegment  
import assemblyai as aai
import uuid

aai.settings.api_key = f"de856eda098840949aef11ab8631b117"

def remove_punctuation(text):
    translator = str.maketrans('', '', string.punctuation)
    cleaned_text = text.translate(translator)
    return cleaned_text

class ContentBlockView(APIView):
    def get(self, request):
        text_with_punctuation = "After discovering time travel via an ancient civilization, an alien race have become hostile and intend to destroy it. In response, the scientists create a time machine which, if complete, will guide the civilizations of both Earth and our universe to freedom"
        cleaned_text = remove_punctuation(text_with_punctuation)
        request.session['text'] = cleaned_text
        return Response({'message': cleaned_text}, status=status.HTTP_201_CREATED)
    
    def post(self, request):
        
        gen_cleaned_text = request.session.get('text', '')
        
        if gen_cleaned_text == '':
            return Response({'message': 'Please generate a text first'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        audio_file = request.FILES['audio_file']
        
        # Check the file extension to determine the format
        file_extension = os.path.splitext(audio_file.name)[1].lower()
        
        if file_extension == '.m4a':
            # Convert M4A to WAV
            audio = AudioSegment.from_file(audio_file, format="m4a")
        else:
            # Assume the file is already in WAV format
            audio = AudioSegment.from_file(audio_file)
        
        audio = audio.set_channels(1) 
        audio = audio.set_frame_rate(16000)  
        audio = audio.set_sample_width(2) 
        
        unique_file_name = f"temp_audio_{uuid.uuid4().hex}.wav"
        temp_wav_path = os.path.join("./temp/", unique_file_name)
        
        
        audio.export(temp_wav_path, format="wav")
        
        transcriber = aai.Transcriber()
        
        # Transcribe the audio file directly from its content
        transcript = transcriber.transcribe(temp_wav_path)
        
        cleaned_text = remove_punctuation(transcript.text)
        
        
        cleaned_words = cleaned_text.split()
        gen_cleaned_words = gen_cleaned_text.split()
        
        response = {}
       
        for index, (word1, word2) in enumerate(zip(cleaned_words, gen_cleaned_words)):
            if word1 == word2:
                response[index] = 'A'
            else:
                response[index] = 'N'
    
        # Check if the length of cleaned_words is less than gen_cleaned_words
        if len(cleaned_words) < len(gen_cleaned_words):
            for i in range(len(cleaned_words), len(gen_cleaned_words)):
                response[i] = 'N'
        
        json_response = json.dumps(response)
        response = json.loads(json_response)
        
        # Calculate the percentage score
        num_words_with_a = sum(1 for value in response.values() if value == 'A')
        total_num_words = len(cleaned_words)
        percentage_score = (num_words_with_a / total_num_words) * 100
        
        percentage_score = str(percentage_score)
        
        os.remove(temp_wav_path)
        
        request.session.pop('text', None)
        
        return Response({'comparison_result': response, 'percentage_score': percentage_score[:5]}, status=status.HTTP_200_OK)
