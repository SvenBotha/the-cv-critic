# The CV Critic
Crafting Resumes That Get Noticed

## Task:
Build a minimal proof-of-concept application that enables a user to upload their CV
and receive back a score out of 10 as well as several recommendations for
improvement. The step-by-step flow is explained below:

**1. The user uploads their CV as a PDF from their computer.** <br>
**2. The application converts the PDF to plain text using ConvertAPI** <br>
  - (a) You will need to create a free account <br>
  - (b) you may also use any other method to convert the PDF to a plain text file

**3. The application then sends the text to an OpenAI assistant for scoring and
suggested improvements.**
  - (a) You will need to log into the assistant with Google SSO using the
provided Gmail account to create your API key and view the structured
format output in the Assistant instructions
  - (b) Do not alter the assistant's instructions
  - (c) Generate a new key for your application - naming convention does not
matter for the key
  - (d) You do not need to account for rate limits or batch queries

**4. Once you receive the feedback, Display a score out of 10 and a list of the
suggested improvements.**
**5. Let the user clear the interface to upload another PDF.**
