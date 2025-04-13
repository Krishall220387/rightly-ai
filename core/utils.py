import os
import openai
from django.conf import settings
import PyPDF2
from docx import Document as DocxDocument
import json
from io import BytesIO
import language_tool_python

def extract_text_from_file(file):
    """Extract text content from different file types."""
    file_extension = os.path.splitext(file.name)[1].lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(file)
    elif file_extension == '.docx':
        return extract_text_from_docx(file)
    else:
        # For txt files or other text-based formats
        return file.read().decode('utf-8')

def extract_text_from_pdf(file):
    """Extract text from PDF files."""
    pdf_reader = PyPDF2.PdfReader(BytesIO(file.read()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file):
    """Extract text from DOCX files."""
    doc = DocxDocument(BytesIO(file.read()))
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def generate_blog_content(topic, tone, target_keywords, documents_content):
    """Generate blog content using OpenAI API."""
    # Initialize OpenAI client
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    # Convert target_keywords to list if it's a string
    if isinstance(target_keywords, str):
        target_keywords = [kw.strip() for kw in target_keywords.split(',') if kw.strip()]

    # Construct the prompt
    prompt = f"""Create a blog article with the following details:
Topic: {topic}
Tone: {tone}
Target Keywords: {', '.join(target_keywords)}
Reference Documents: {documents_content}

Requirements:
1. SEO-optimized content
2. Natural, human-like writing style
3. Compelling title
4. Strategic keyword usage
5. Structured outline with H2 and H3 tags
6. Comprehensive, editable draft

Please provide the output in the following JSON structure:
{{
    "blog_title": "Your generated title",
    "keywords": {{
        "user_keywords": {json.dumps(target_keywords)},
        "additional_keywords": []
    }},
    "blog_outline": "Your outline with H2/H3 tags",
    "blog_draft": "Your complete blog draft"
}}"""

    try:
        print(f"Sending request to OpenAI API with topic: {topic}")
        
        # Call OpenAI API with the new client format
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a professional content writer and SEO expert. Always provide output in valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )

        print("Received response from OpenAI API")
        
        # Extract and parse the response
        content = response.choices[0].message.content
        print(f"Raw API response content: {content[:200]}...")
        
        try:
            # Parse the JSON response
            result = json.loads(content)
            
            # Validate the response structure
            required_keys = ['blog_title', 'keywords', 'blog_outline', 'blog_draft']
            missing_keys = [key for key in required_keys if key not in result]
            if missing_keys:
                raise ValueError(f"Missing required keys in response: {missing_keys}")
            
            # Ensure keywords structure is correct
            if 'keywords' not in result or not isinstance(result['keywords'], dict):
                result['keywords'] = {
                    'user_keywords': target_keywords,
                    'additional_keywords': []
                }
            else:
                # Ensure both keyword lists exist
                if 'user_keywords' not in result['keywords']:
                    result['keywords']['user_keywords'] = target_keywords
                if 'additional_keywords' not in result['keywords']:
                    result['keywords']['additional_keywords'] = []
            
            print("Successfully validated response structure")
            return result
            
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {str(e)}")
            # Create a fallback response
            return {
                'blog_title': topic,
                'keywords': {
                    'user_keywords': target_keywords,
                    'additional_keywords': []
                },
                'blog_outline': 'Error generating outline',
                'blog_draft': 'Error generating draft'
            }

    except Exception as e:
        print(f"Error in generate_blog_content: {str(e)}")
        if hasattr(e, 'response'):
            print(f"OpenAI API Response: {e.response}")
        raise Exception(f"Error generating blog content: {str(e)}")

def check_grammar(text):
    """
    Check grammar in the given text and return suggestions.
    Returns a list of dictionaries containing grammar suggestions.
    """
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    
    suggestions = []
    for match in matches:
        suggestion = {
            'from': match.offset,
            'to': match.offset + match.errorLength,
            'message': match.message,
            'replacements': match.replacements,
            'context': match.context,
            'context_offset': match.contextOffset
        }
        suggestions.append(suggestion)
    
    return suggestions 