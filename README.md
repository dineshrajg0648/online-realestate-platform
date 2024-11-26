# Travel Planner

A web application for planning and managing your trips.

## Features

- Create and manage travel plans
- Track trip dates and destinations
- Add descriptions and notes for each trip
- Modern and responsive user interface

## Installation

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to `http://localhost:5000`

## Technologies Used

- Backend: Flask
- Database: SQLite with SQLAlchemy
- Frontend: HTML, CSS, JavaScript
- UI Framework: Bootstrap 5

## Project Structure

```
travels/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── static/            # Static files
│   ├── css/          
│   │   └── style.css  # Custom styles
│   └── js/
│       └── main.js    # Frontend JavaScript
├── templates/         # HTML templates
│   └── index.html    
└── README.md         # Project documentation
```
