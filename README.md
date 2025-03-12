# Todo List Flask App

This is a simple Flask application that provides an API for managing todo lists and todo entries. It demonstrates how to represent todo lists and entries using Python data structures and implement REST API endpoints with Flask. It also uses SQLLite to save the data so it will not be gone after a server restart

The app is also deployed on a live server so you can make actual requests to the live server.

## Requirements

- Docker

## Usage

1. Clone the repository:
    ```shell
   git clone <https://github.com/ilsit/legendary-list>

2. Navigate to the project directory:
    ```shell
   cd todo_api_list

3. Build the Docker image:
    ```shell
    docker build -t todo_api_list .

4. Run the Docker container:
    ```shell
    docker run --restart=always -p 5000:5000 todo_api_list

5. Access the API endpoints:

- Open your web browser and go to [http://localhost:5000](http://localhost:5000) to view the Swagger documentation and interact with the API using the Swagger UI.

6. Optional:
- if you want to deploy the script and develop it further 

  ```shell
  # Create a virtual environment (optional but recommended)
  python -m venv venv

   # Activate the virtual environment:
   # On macOS/Linux:
   source venv/bin/activate

   # On Windows:
   venv\Scripts\activate

   # Upgrade pip (just in case)
   pip install --upgrade pip

   # Install dependencies
   pip install -r requirements.txt



## API Endpoints

- **GET /todo-list**: Retrieve all todo lists.
- **POST /todo-list**: Create a new todo list.
- **GET /todo-list/{list_id}**: Retrieve a specific todo list by its ID.
- **DELETE /todo-list/{list_id}**: Delete a specific todo list and all its items.
- **GET /todo-list/{list_id}/entries**: Retrieve all entries of a specific todo list.
- **POST /todo-list/{list_id}/entry**: Add a new entry to a specific todo list.
- **PUT /todo-list/{list_id}/entry/{entry_id}**: Update an existing entry in a specific todo list.
- **DELETE /todo-list/{list_id}/entry/{entry_id}**: Delete an entry from a specific todo list.

## License

This project is licensed under the [MIT License](LICENSE.txt).

## Dockerfile

```dockerfile
# Use a stable Python base image
FROM python:3.11-alpine

# Set the working directory in the container
WORKDIR /app

# Install required system dependencies
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev sqlite sqlite-dev

# Install required Python dependencies
RUN pip install --no-cache-dir flask flask-sqlalchemy pyyaml

# Copy the Flask application code into the container
COPY . .

# Expose the port that the Flask server will be running on
EXPOSE 5000

# Start the Flask server
CMD ["python", "webserver.py"]


# Set the entrypoint command to run the Flask app
CMD ["python", "app.py"]
