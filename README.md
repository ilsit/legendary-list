# Todo List Flask App

This is a simple Flask application that provides an API for managing todo lists and todo entries. It demonstrates how to represent todo lists and entries using Python data structures and implement REST API endpoints with Flask.

## Requirements

- Docker

## Usage

1. Clone the repository:
    ```shell
   git clone <https://github.com/ilsit/todo-list.git>

2. Navigate to the project directory:
    ```shell
   cd todo-list-flask-app

3. Build the Docker image:
    ```shell
    docker build -t todo-list-flask-app .

4. Run the Docker container:
    ```shell
    docker run --restart=always -p 5000:5000 todo-list-flask-app

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
  
   # if you want to run the db docker-compose is requiered
   docker compose up -d
   # then enter/change credentials to connect to db in your script 



## API Endpoints

- **GET /todo-list/{list_id}**: Retrieve a specific todo list by its ID.
- **DELETE /todo-list/{list_id}**: Delete a specific todo list by its ID.
- **POST /todo-list**: Create a new todo list.
- **POST /todo-list/{list_id}/item**: Add a new item to a specific todo list.
- **PUT /todo-list/{list_id}/items/{item_id}**: Update an existing item in a specific todo list.
- **DELETE /todo-list/{list_id}/items/{item_id}**: Delete an item from a specific todo list.
- **GET /lists**: Get all todo lists.

## License

This project is licensed under the [MIT License](LICENSE).

## Dockerfile

```dockerfile
# Use the official Python image as the base image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY . .

# Expose the port that the Flask app will listen on
EXPOSE 5000

# Set the entrypoint command to run the Flask app
CMD ["python", "app.py"]
