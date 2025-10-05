# VocabMate Backend

A Django REST Framework API for vocabulary learning application with MongoDB support.

## Prerequisites

- Python 3.8+
- MongoDB (local installation or MongoDB Atlas)
- Virtual environment

## Setup Instructions

### 1. Install MongoDB

#### Local MongoDB Installation:

- **Windows**: Download from [MongoDB Community Server](https://www.mongodb.com/try/download/community)
- **macOS**: `brew install mongodb-community`
- **Linux**: Follow [MongoDB Installation Guide](https://docs.mongodb.com/manual/installation/)

#### MongoDB Atlas (Cloud):

- Create account at [MongoDB Atlas](https://www.mongodb.com/atlas)
- Create a free cluster
- Get connection string

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the root directory:

#### For Local MongoDB:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
MONGODB_NAME=vocab_mate
MONGODB_HOST=mongodb://localhost:27017/
MONGODB_USERNAME=
MONGODB_PASSWORD=
MONGODB_AUTH_SOURCE=admin
MONGODB_AUTH_MECHANISM=SCRAM-SHA-1
```

#### For MongoDB Atlas:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
MONGODB_NAME=vocab_mate
MONGODB_HOST=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_USERNAME=your-atlas-username
MONGODB_PASSWORD=your-atlas-password
MONGODB_AUTH_SOURCE=admin
MONGODB_AUTH_MECHANISM=SCRAM-SHA-1
```

### 5. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Run Server

```bash
python manage.py runserver
```

## API Endpoints

### Authentication

- `POST /api/register/` - User registration
- `POST /api/login/` - User login
- `GET /api/profile/` - Get user profile
- `GET /api/stats/` - Get user learning statistics

### Words

- `GET /api/words/` - List all words (with filtering and search)
- `POST /api/words/` - Create new word
- `GET /api/words/{id}/` - Get word details
- `PUT /api/words/{id}/` - Update word
- `DELETE /api/words/{id}/` - Delete word

### User Progress

- `GET /api/progress/` - Get user's learning progress
- `POST /api/progress/` - Mark word as learned/in progress
- `GET /api/progress/{id}/` - Get specific progress
- `PUT /api/progress/{id}/` - Update progress
- `DELETE /api/progress/{id}/` - Delete progress

## Features

- **MongoDB Integration**: Full MongoDB support with Djongo
- **JWT Authentication**: Secure token-based authentication
- **CORS Support**: Frontend integration ready
- **Advanced Filtering**: Search and filter capabilities
- **Pagination**: Efficient data loading
- **User Progress Tracking**: Learning analytics and streaks
- **MongoDB-Specific Features**:
  - List fields for tags, synonyms, antonyms
  - Dictionary fields for flexible data storage
  - Optimized indexes for performance
  - ObjectId references
- **Admin Interface**: Django admin with MongoDB support
- **API Documentation**: DRF browsable API

## Testing the API

You can test the API using:

- Django REST Framework browsable API at `http://localhost:8000/api/`
- Postman or similar API testing tools
- Frontend application

## Admin Interface

Access the admin interface at `http://localhost:8000/admin/` using your superuser credentials.
