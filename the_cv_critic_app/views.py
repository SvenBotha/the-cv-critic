"""
views.py

This module contains the views for the CV Critic application. It handles the uploading and processing of CVs,
including converting PDF files to text and using the OpenAI API to review and provide feedback on the CVs.

Functions:
    convert_pdf_to_text(pdf_path): Converts a PDF file to text using ConvertAPI.
    process_cv(text): Processes the text of a CV using the OpenAI assistant.
    upload_cv(request): Handles the CV upload request, converts the PDF to text, and processes the CV text.

Author: Sven Botha
Date: 17 February 2025
"""

from .forms import CVUploadForm 
from django.http import JsonResponse
from django.shortcuts import render, redirect

import os
import re
import json
import time
import openai
import logging
import tempfile
import convertapi

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

try:
    assistant = client.beta.assistants.create(
        name="CV Reviewer Assistant",
        instructions="You are an expert CV reviewer. Use your knowledge of recruitment to provide feedback on a CV. Score the CV out of 10 and provide recommendations for improvement. Return the score and recommendations in the following JSON format:\n```json\n{\n  \"score\": <score>, \n  \"recommendations\": [<recommendation1>, <recommendation2>, ...]\n}\n```",
        model="gpt-4-turbo-preview",
        tools=[{"type": "file_search"}],
    )
    logging.info(f"Assistant created successfully with ID: {assistant.id}")
except Exception as e:
    try:
        error_data = e.response.json()
        error_code = error_data.get('error', {}).get('code')
        error_message = "Error code: " + error_code + "\n" + error_data.get('error', {}).get('message')
    except AttributeError:
        error_message = str(e)

    logging.error("Error initializing OpenAI Assistant:")
    logging.error(error_message)

    assistant = None

convertapi.api_key = os.getenv("CONVERTAPI_API_KEY")

def convert_pdf_to_text(pdf_path):
    convertapi.api_credentials = os.environ.get('CONVERTAPI_API_KEY')

    try:
        # Convert PDF to text
        result = convertapi.convert('txt', {'File': pdf_path}, from_format='pdf')

        # Create a temporary file to store the output
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            output_file = temp_file.name

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
        # Create an openai thread
        thread = client.beta.threads.create()

        # Send the CV text to the assistant
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=text,
        )

        # Run the assistant
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
            time.sleep(1) 
        
        # Retrieve the assistant's response
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        assistant_response = next((msg.content[0].text.value for msg in messages.data if msg.role == "assistant"), "")

        # Extract only the JSON content
        if assistant_response.startswith("```json") and assistant_response.endswith("```"):
            assistant_response = re.sub(r"```json|```", "", assistant_response).strip()

        # Debugging: Print the cleaned-up response
        logging.debug("Cleaned Assistant Response:", assistant_response)

        # Parse the JSON response
        try:
            data = json.loads(assistant_response) 
            score = data.get('score', 0)
            recommendations = data.get('recommendations', [])

        except json.JSONDecodeError:
            score = 0
            recommendations = ["Could not parse the assistant's response. Ensure it is valid JSON."]

        return score, recommendations

    except Exception as e:
        return 0, [f"Error processing CV: {e}"]

def upload_cv(request):
    # Process the uploaded CV
    if request.method == 'POST':
        # Validate the uploaded file
        form = CVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded file to a temporary location
            cv_file = request.FILES['cv']
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                for chunk in cv_file.chunks():
                    temp_file.write(chunk)
                pdf_path = temp_file.name
            
            # Convert the PDF to text
            text = convert_pdf_to_text(pdf_path)

            # Clean up the temporary file
            os.remove(pdf_path)
            
            if "Error converting PDF" in text:
                return JsonResponse({'error': text})
            
            # Process the CV text using openai assistant
            score, recommendations = process_cv(text)
            return JsonResponse({'score': score, 'recommendations': recommendations})
        else:
            return JsonResponse({'error': 'Invalid form'})
    else:
        form = CVUploadForm()
    return render(request, 'the_cv_critic_app/index.html', {'form': form})
