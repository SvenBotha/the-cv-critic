
#############
## imports ##
#############

from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import CVUploadForm 

import os
import json
import openai
import convertapi
import tempfile
import time

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

try:
    assistant = client.beta.assistants.create(
        name="CV Reviewer Assistant",
        instructions="You are an expert CV reviewer. Use your knowledge of recruitment to provide feedback on a CV. Score the CV out of 10 and provide recommendations for improvement. Return the score and recommendations in the following JSON format:\n```json\n{\n  \"score\": <score>, \n  \"recommendations\": [<recommendation1>, <recommendation2>, ...]\n}\n```",
        model="gpt-4-turbo-preview",
        tools=[{"type": "file_search"}],
    )
    print(f"Assistant created successfully with ID: {assistant.id}")
except Exception as e:
    print(f"Error initializing OpenAI Assistant: {e}")
    assistant = None  # If creation fails, set assistant to None

convertapi.api_key = os.getenv("CONVERTAPI_API_KEY")
import convertapi
import os
import tempfile

def convert_pdf_to_text(pdf_path):
    convertapi.api_credentials = os.environ.get('CONVERTAPI_API_KEY')

    try:
        # Convert PDF to text
        result = convertapi.convert('txt', {'File': pdf_path}, from_format='pdf')

        # Create a temporary file to store the output
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            output_file = temp_file.name  # Store the path of the temp file

        # Save the converted file to the temp location
        result.save_files(output_file)

        # Read the text from the saved file
        with open(output_file, 'r', encoding='utf-8') as file:
            text = file.read()

        # Clean up temporary file
        os.remove(output_file)

        return text

    except Exception as e:
        return f"Error converting PDF: {e}"


def process_cv(text):
    if assistant is None:
        return 0, ["Error: Could not create/retrieve OpenAI assistant."]
    try:
        thread = client.beta.threads.create()
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=text,
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )
        
        # Polling for completion
        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            if run.status == "completed":
                break
            elif run.status == "failed":
                return 0, ["Error: Assistant failed to process CV"]
            time.sleep(1)  # Avoid excessive API calls
        
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        assistant_response = next((msg.content[0].text.value for msg in messages.data if msg.role == "assistant"), "")
        # Debugging: Print raw assistant response
        print("Raw Assistant Response:", assistant_response)

        import re

        # Extract only the JSON content
        if assistant_response.startswith("```json") and assistant_response.endswith("```"):
            assistant_response = re.sub(r"```json|```", "", assistant_response).strip()

        # Debugging: Print the cleaned-up response
        print("Cleaned Assistant Response:", assistant_response)

        try:
            data = json.loads(assistant_response)  # Ensure it's valid JSON
            score = data.get('score', 0)
            recommendations = data.get('recommendations', [])

        except json.JSONDecodeError:
            score = 0
            recommendations = ["Could not parse the assistant's response. Ensure it is valid JSON."]

        return score, recommendations

    except Exception as e:
        return 0, [f"Error processing CV: {e}"]

def upload_cv(request):
    if request.method == 'POST':
        form = CVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            cv_file = request.FILES['cv']
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                for chunk in cv_file.chunks():
                    temp_file.write(chunk)
                pdf_path = temp_file.name
            
            text = convert_pdf_to_text(pdf_path)
            os.remove(pdf_path)
            
            if "Error converting PDF" in text:
                return JsonResponse({'error': text})
            
            score, recommendations = process_cv(text)
            return JsonResponse({'score': score, 'recommendations': recommendations})
        else:
            return JsonResponse({'error': 'Invalid form'})
    else:
        form = CVUploadForm()
    return render(request, 'the_cv_critic_app/index.html', {'form': form})
