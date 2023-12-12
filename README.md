# pokemon code 

## Overview

This project demonstrates the usage of FastAPI with Uvicorn for building a RESTful API.

## Setup Instructions

### Prerequisites

- Python 3.8+
- Pip (Python package manager)

### Installation

1. Clone the repository:
   `git clone git@github.com:ImlogR/pkemonGO.git`

2. Install the requirements using pip (Perfer to install these inside a virtual environment :))
    `pip install -r requirements.txt`

3. Setup the .env file in the project directory as of the .env_demo file content with actual credentials

4. Setup the database or just run the docker-compose file present in the directory as;
    `docker-compose up`

5. Once database is ready to accept connections then run the following script to start the uvicorn service
    `uvicorn myapi:app`
    the server must be running on your http://localhist:8000 or http://127.0.0.1:8000 for now
    you can view the route /api/v1/pokemons for complete pokemon list
    I recommend to use FastAPI swagger UI for convenience for passing parameters at http://localhost:8000/docs or http://127.0.0.1:8000/docs
