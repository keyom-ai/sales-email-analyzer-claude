# app.py
import os
import sys
import traceback
from flask import Flask, request, render_template_string
from anthropic import Anthropic

app = Flask(__name__)

# Initialize the Anthropic client
try:
    anthropic = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
except Exception as e:
    print(f"Error initializing Anthropic client: {str(e)}")
    anthropic = None

# HTML templates as strings with improved styling
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Analyzer</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
        }
        form {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            resize: vertical;
        }
        input[type="submit"] {
            display: block;
            width: 100%;
            padding: 10px;
            background-color: #3498db;
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
        }
        input[type="submit"]:hover {
            background-color: #2980b9;
        }
    </style>
</head>
<body>
    <h1>Email Analyzer</h1>
    <form method="POST">
        <textarea name="email_content" rows="10" placeholder="Paste your email content here"></textarea>
        <input type="submit" value="Analyze">
    </form>
</body>
</html>
"""

RESULT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analysis Result</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
        }
        .result {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        a {
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background-color: #3498db;
            color: #fff;
            text-decoration: none;
            border-radius: 4px;
        }
        a:hover {
            background-color: #2980b9;
        }
    </style>
</head>
<body>
    <h1>Analysis Result</h1>
    <div class="result">
        <pre>{{ analysis }}</pre>
    </div>
    <a href="/">Analyze Another Email</a>
</body>
</html>
"""

ERROR_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }
        h1 {
            color: #e74c3c;
            text-align: center;
        }
        .error {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        a {
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background-color: #3498db;
            color: #fff;
            text-decoration: none;
            border-radius: 4px;
        }
        a:hover {
            background-color: #2980b9;
        }
    </style>
</head>
<body>
    <h1>An Error Occurred</h1>
    <div class="error">
        <pre>{{ error_message }}</pre>
    </div>
    <a href="/">Return to Home</a>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def analyze_email():
    if request.method == "POST":
        email_content = request.form["email_content"]
        
        try:
            if anthropic is None:
                raise Exception("Anthropic client is not initialized")

            # Improved prompt for more comprehensive analysis
            prompt = f"""
            Please analyze the following sales email for professionalism and effectiveness. Provide a comprehensive evaluation covering the following aspects:

            1. Overall Impression: Give a brief summary of the email's effectiveness.
            2. Tone and Professionalism: Assess the email's tone. Is it appropriate for a business context?
            3. Clarity and Coherence: Evaluate how well the message is communicated. Is it easy to understand?
            4. Structure and Organization: Comment on the email's layout and flow of information.
            5. Opening and Closing: Analyze the effectiveness of the email's introduction and conclusion.
            6. Call-to-Action: Is there a clear next step for the recipient? How compelling is it?
            7. Personalization: Does the email feel tailored to the recipient?
            8. Grammar and Spelling: Note any errors or areas for improvement.
            9. Length and Conciseness: Is the email appropriately brief while still conveying all necessary information?
            10. Suggestions for Improvement: Provide specific recommendations to enhance the email's effectiveness.

            Here's the email content:

            {email_content}

            Please provide your analysis in a structured format, addressing each of the points above.
            """

            # Call Claude API for analysis using the Messages API
            message = anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            analysis = message.content[0].text
            
            return render_template_string(RESULT_TEMPLATE, analysis=analysis)
        except Exception as e:
            error_message = f"An error occurred: {str(e)}\n\nTraceback:\n{''.join(traceback.format_tb(e.__traceback__))}"
            print(error_message, file=sys.stderr)
            return render_template_string(ERROR_TEMPLATE, error_message=error_message), 500
    
    return render_template_string(INDEX_TEMPLATE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
