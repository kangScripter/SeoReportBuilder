# SEO Report Builder

A Flask-based web application that generates SEO reports by analyzing Google Search Console data and providing query intent analysis using OpenAI's API.

## Features

- 🔐 Google OAuth2 Authentication
- 📊 Search Console Data Integration
- 🤖 AI-Powered Query Intent Analysis
- 📈 Time-based Metrics (28D, 3M)
- 📱 Responsive Drag & Drop Interface
- 🔄 Real-time Data Updates
- 📄 Paginated Results
- 💾 Data Caching

## Prerequisites

- Python 3.8+
- Google Search Console Account
- OpenAI API Key
- Google OAuth2 Credentials

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd SEOReport
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
   - Copy `.env.example` to `.env`
   - Update the following variables in `.env`:
     ```
     OPENAI_KEY=your_openai_api_key
     SECRET_KEY=your_secret_key
     ```

5. Set up Google OAuth:
   - Create a project in Google Cloud Console
   - Enable Google Search Console API
   - Create OAuth 2.0 credentials
   - Download `client_secrets.json` and place it in the project root

## Usage

1. Start the development server:
```bash
flask run
```

2. Access the application at `http://localhost:5000`

3. Sign in with your Google account

4. Build your report:
   - Select a property from Google Search Console
   - Choose time range
   - Drag and drop metrics
   - Generate report

## Project Structure

```
SEOReport/
├── core/
│   ├── __init__.py
│   ├── auth.py
│   ├── routes.py
│   ├── utils.py
│   ├── report_builder/
│   │   ├── routes.py
│   │   └── templates/
│   └── templates/
│       ├── base.html
│       ├── home.html
│       └── report_builder/
├── .env
├── .env.example
├── client_secrets.json
├── client_secrets.example.json
├── requirements.txt
└── web.py
```

## API Endpoints

- `GET /` - Home page
- `GET /report` - Report builder interface
- `GET /reports/api/properties` - List Search Console properties
- `POST /reports/api/generate-report` - Generate SEO report
- `GET /authorize` - OAuth2 authorization
- `GET /oauth2callback` - OAuth2 callback
- `GET /revoke` - Revoke OAuth2 credentials
- `GET /clear` - Clear session credentials

## Metrics Available

- Clicks (28D, 3M)
- Impressions (28D, 3M)
- CTR (28D, 3M)
- Position (28D, 3M)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Search Console API
- OpenAI API
- Flask Framework
- Bootstrap CSS Framework 