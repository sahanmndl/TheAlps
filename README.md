# The Alps

Yes, the mountain range (and I mean it :)

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT
- **Market Data**: Indian Stock Market API
- **AI Integration**: OpenAI GPT-5

## Setup

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   Create a `.env` file:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/the_alps
   SECRET_KEY=your_jwt_secret_key
   ALGORITHM=your_jwt_decode_algorithm
   ACCESS_TOKEN_EXPIRE_MINUTES=jwt_access_token_validity_in_minutes
   REFRESH_TOKEN_EXPIRE_DAYS=jwt_refresh_token_validity_in_days
   INDIAN_STOCK_MARKET_API_KEY=your_api_key
   OPENAI_API_KEY=your_openai_key
   ```

4. **Database Setup**
   ```bash
   # Create database
   createdb the_alps
   
   # Run migrations
   alembic upgrade head
   ```

5. **Run Development Server**
   ```bash
   uvicorn main:app --reload
   ```

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
the_alps/
├── alembic/                 # Database migrations
├── app/
│   ├── api/                # API endpoints
│   ├── core/               # Core functionality
│   ├── db/                 # Database setup
│   ├── models/            # Pydantic models
│   ├── schemas/           # SQLAlchemy models
│   └── services/          # Business logic
├── .env                   # Environment variables
├── .gitignore            # Git ignore file
├── alembic.ini           # Alembic configuration
├── main.py               # Application entry point
└── requirements.txt      # Project dependencies
```

## Development

1. **Create New Migration**
   ```bash
   alembic revision --autogenerate -m "description"
   ```

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/feature-name`)
3. Commit changes (`git commit -am 'Add feature'`)
4. Push to branch (`git push origin feature/feature-name`)
5. Create Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.