import openai, os
import re
from django.conf import settings




def remove_punctuation(text):
    text = re.sub(r'[^\w\s]', '', text)
    # Remove '\n' and words between '\n'
    text = re.sub(r'\n\s*\w+\s*\n', ' ', text)
    return text

def generate_story(genre):
    

    # Use f-strings for string interpolation to include the genre variable
    prompt = f"Write a short story on any one of the genre {genre} with max word count of fifty words finish the sentence once started , don't break the flow of the story."

    # Generate a response using the OpenAI API
    response = openai.Completion.create(
        engine="text-davinci-002",  # Choose an appropriate engine
        prompt=prompt,
        max_tokens=50,  # Adjust the desired response length
        n=1,  # Number of responses to generate
        stop=None,  # You can specify a stopping criterion if needed
        temperature=0.7,  # Adjust the temperature
    )
    
    generated_text = response.choices[0].text

    # Print the generated response
    print(generated_text)
    
    print(genre)
    return generated_text[2:]
    
    
if __name__ == "__main__":
    generate_story('fantasy')