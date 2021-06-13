# Take Home Assignment for CB Insights

REST interface for a custom cache, which stores JSON objects(strings) in the server’s memory, that can be accessed via the API. Built in Flask.

## Installation

1. Clone the repository

2. With python >=3.6, install pipenv

`python3 -m pip install pipenv`

3. Inside the repository folder, create your .env from the example

`cp env.example .env`

4. Install the repositories using pipenv

`pipenv install`

5. Start the virtual environment using pipenv

`pipenv install`

6. Export the main webapp into the invironment for flask to find it

`export FLASK_APP=src/app.py`

7. Run flask

`flask run`

8. In default configurations, the webapp should be open al localhost:5000