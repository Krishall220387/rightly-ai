# Rightly.ai - AI-Powered Blog Generation Platform

Rightly.ai is an intelligent content creation platform that helps marketers and content writers generate high-quality, SEO-optimized blog articles in minutes. The platform uses advanced AI to analyze your existing content and create human-like blog posts that outperform competitors.

## Features

- **AI-Powered Blog Generation**: Generate complete blog posts with just a topic and keywords
- **Context-Aware Content**: Upload documents to provide context about your products/services
- **SEO Optimization**: AI suggests additional keywords based on competitor research
- **Human-Like Content**: Generated content passes AI detection tests
- **Grammar Checking**: Built-in grammar checker for content refinement
- **Document Management**: Upload and manage reference documents
- **Easy Editing**: Edit generated content with a user-friendly interface
- **Word Export**: Download blogs in Microsoft Word format

## Technical Stack

- **Backend**: Django/Python
- **Frontend**: HTML, CSS (Bootstrap), JavaScript
- **Database**: SQLite
- **AI Integration**: OpenAI GPT-4
- **Authentication**: Django built-in auth

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Krishall220387/rightly-ai.git
cd rightly-ai
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory and add:
```
OPENAI_API_KEY=your_api_key_here
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start the development server:
```bash
python manage.py runserver
```

## Usage

1. Register/Login to your account
2. Upload reference documents about your products/services
3. Create a new blog by providing:
   - Blog topic
   - Target keywords
   - Writing tone
   - Select reference documents
4. The AI will generate:
   - Blog title
   - Additional keywords
   - Blog outline
   - Complete blog draft
5. Edit the generated content as needed
6. Check grammar and make corrections
7. Save or download the blog

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 