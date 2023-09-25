from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import string, os, json
from pydub import AudioSegment  
from .models import User, Content
import assemblyai as aai
import uuid
import openai
from .story_generaton import generate_story, remove_punctuation


aai.settings.api_key = os.environ.get('ASSEMBLYAI_API_KEY')


class SignUpView(APIView): 
    
    def post(self, request): 
        data = request.data
        
        user_data = User.objects.filter(user_id=data['user_id'])
        
        if user_data.exists():
            
            return Response({'message': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User(name=data['name'], age=data['age'], email=data['email'], tags=data['tags'], user_id=data['user_id'])
        
        if user:
            user.save()
            
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        
        return Response({'message': 'User not created'}, status=status.HTTP_400_BAD_REQUEST)
        

class ContentBlockView(APIView):
    def get(self, request):

        
        data = request.data 
        
        if data:
            user_data = User.objects.filter(user_id=data['user_id'])
            
            text_with_punctuation = generate_story(user_data[0].tags)
            
            cleaned_text = remove_punctuation(text_with_punctuation)
            
            content_data = Content(user_id=data['user_id'], content=cleaned_text)
            
            content_data.save()
            
            return Response({'message': cleaned_text}, status=status.HTTP_201_CREATED)
        
        return Response({'message': 'Please give all the credientials'}, status=status.HTTP_200_OK)
    
    def post(self, request):
        
        data = request.POST.get('user_id')

        
        content_data = Content.objects.filter(user_id=data).last()
        
        
        if content_data.audio_location:
            
            return Response({'message': 'Audio file already exists, generate another story or content'}, status=status.HTTP_400_BAD_REQUEST)
        
                    
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
        gen_cleaned_words = content_data.content.split()
        

        response = []

        for word1, word2 in zip(cleaned_words, gen_cleaned_words):
            if word1 == word2:
                response.append({"is_correct": "A"})
            else:
                response.append({"is_correct": "N"})

        # Add "N" for extra words in gen_cleaned_words
        if len(cleaned_words) < len(gen_cleaned_words):
            for i in range(len(cleaned_words), len(gen_cleaned_words)):
                response.append({"is_correct": "N"})

        
        json_response = json.dumps(response)
        response = json.loads(json_response)
        
        
        content_data.audio_location = temp_wav_path
        
        content_data.save()
        
        return Response({'comparison_result': response}, status=status.HTTP_200_OK)