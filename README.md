# Email Personalization Tool

An AI-powered email personalization tool for sales outreach that generates highly personalized emails based on prospect data, company research, and product usage metrics.

## Features

- AI-powered email personalization using OpenAI GPT-4
- Prospect and company data management
- Email template management
- Automated email sending with tracking
- Custom data integration support
- Modern FastAPI backend with React frontend

## Setup

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example` and fill in your configuration:
- OpenAI API key
- SMTP settings
- Database configuration
- Security settings

4. Start the backend server:
```bash
uvicorn app.main:app --reload
```

The backend API will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will be available at http://localhost:3000

## API Endpoints

- `GET /`: Welcome message
- `GET /health`: Health check
- `POST /api/prospects/`: Create new prospect
- `GET /api/prospects/{id}`: Get prospect details
- `GET /api/prospects/`: List all prospects

## Development

The project structure follows modern practices with:
- FastAPI for the web framework
- SQLAlchemy for database operations
- Pydantic for data validation
- OpenAI for AI-powered personalization
- React for the frontend
- TypeScript for type safety

## Security

- API key authentication
- Rate limiting
- Input validation
- Secure email handling
- Environment variable protection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 

from dotenv import load_dotenv
load_dotenv() 