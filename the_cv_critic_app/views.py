from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import CVUploadForm 
import os
import json
import openai
import convertapi
import tempfile

openai.api_key = os.getenv("OPENAI_API_KEY")

def convert_pdf_to_text(pdf_path):
    convertapi.api_credentials = os.environ.get('CONVERTAPI_API_KEY')
    with tempfile.NamedTemporaryFile(mode='w+t', suffix='.txt', delete=False) as temp_file: # Create a temporary file
        convertapi.convert('txt', {
            'File': pdf_path
        }, from_format = 'pdf').save_files(temp_file.name) # Save to the temporary file
        text = temp_file.read() # Read the content of the temporary file
        temp_file_name = temp_file.name # Store the name to remove it later
    os.remove(temp_file_name) # Remove the Temporary file
    return text

def process_cv(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a CV analysis assistant. Score the CV out of 10 and provide recommendations for improvement. Return the score and recommendations in the following JSON format:\n```json\n{\n  \"score\": <score>, \n  \"recommendations\": [<recommendation1>, <recommendation2>, ...]\n}\n```"},
                {"role": "user", "content": text}
            ]
        )

        assistant_response = response['choices'][0]['message']['content']

        try:
            data = json.loads(assistant_response)
            score = data.get('score', 0)
            recommendations = data.get('recommendations', [])

        except json.JSONDecodeError:
            score = 0
            recommendations = ["Could not parse the assistant's response. Ensure it is valid JSON."]

        return score, recommendations

    except Exception as e:  # Add an except block here!
        return 0, [f"Error processing CV with OpenAI: {e}"]



def upload_cv(request):
    if request.method == 'POST':
        form = CVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            cv_file = request.FILES['cv']
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file: # Create a temporary file
                for chunk in cv_file.chunks():
                    temp_file.write(chunk)
                pdf_path = temp_file.name # Store the name of the file
            
            text = convert_pdf_to_text(pdf_path)
            if "Error converting PDF" in text:
                os.remove(pdf_path) # Remove the Temporary file
                return JsonResponse({'error': text})

            score, recommendations = process_cv(text)
            os.remove(pdf_path) # Remove the Temporary file

            return JsonResponse({'score': score, 'recommendations': recommendations})
        else:
            return JsonResponse({'error': 'Invalid form'})
    else:
        form = CVUploadForm()
    return render(request, 'the_cv_critic_app/index.html', {'form': form})