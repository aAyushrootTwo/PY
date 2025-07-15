from flask import Flask, request, render_template, jsonify
import google.generativeai as genai
import os
import re

app = Flask(__name__)

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyBkUxc1zRgvumzIRaqOyR9vTYt2mEnOxDI"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-2.0-flash')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_blog_post():
    try:
        # Get form data
        topic = request.form.get('topic', '').strip()
        tone = request.form.get('tone', 'professional')
        length = request.form.get('length', 'medium')
        keywords = request.form.get('keywords', '').strip()
        
        # Validate input
        if not topic:
            return jsonify({'success': False, 'error': 'Topic is required'})
        
        # Create prompt based on user inputs
        prompt = create_blog_prompt(topic, tone, length, keywords)
        
        # Generate content using Gemini
        response = model.generate_content(prompt)
        
        if response.text:
            # Clean and format the generated content
            formatted_content = format_blog_content(response.text)
            return jsonify({'success': True, 'content': formatted_content})
        else:
            return jsonify({'success': False, 'error': 'Failed to generate content'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def create_blog_prompt(topic, tone, length, keywords):
    """Create a detailed prompt for the Gemini API"""
    
    # Map length to word count
    length_mapping = {
        'short': '300-500 words',
        'medium': '500-800 words',
        'long': '800-1200 words'
    }
    
    word_count = length_mapping.get(length, '500-800 words')
    
    prompt = f"""
    Write a comprehensive and engaging blog post about "{topic}".
    
    Requirements:
    - Writing tone: {tone}
    - Length: {word_count}
    - Include a catchy title
    - Structure with clear headings and subheadings
    - Write in a {tone} tone throughout
    - Make it informative and valuable to readers
    - Include practical tips or insights where relevant
    - End with a compelling conclusion
    """
    
    if keywords:
        prompt += f"\n- Naturally incorporate these keywords: {keywords}"
    
    prompt += """
    
    Format the response as follows:
    1. Start with an engaging title
    2. Write an introduction that hooks the reader
    3. Use clear headings for main sections
    4. Include bullet points or numbered lists where appropriate
    5. Write a strong conclusion
    
    Make sure the content is original, well-researched, and provides real value to readers.
    """
    
    return prompt

def format_blog_content(content):
    """Format the generated content for better display"""
    
    # Remove extra whitespace
    content = re.sub(r'\n\s*\n', '\n\n', content)
    
    # Format headings (assuming they start with # or are in ALL CAPS)
    content = re.sub(r'^#\s*(.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^##\s*(.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^###\s*(.+)$', r'<h4>\1</h4>', content, flags=re.MULTILINE)
    
    # Format bold text
    content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\