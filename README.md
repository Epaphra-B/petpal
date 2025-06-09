# PetPal - Your Pet Care Companion

## Description

PetPal is a web application designed to help pet owners manage their pet's health, track reminders, and maintain a checklist of tasks.

## Features

- User authentication (Register, Login, Logout)
- Pet profiles (Add, Edit, View)
- Health records management
- Reminder system
- Task checklist
- Care tips based on pet species

## Technologies Used

- Python
- Flask
- SQLAlchemy
- Flask-Login
- Flask-WTF
- Bootstrap 5

## Setup Instructions

1.  **Clone the repository:**

    ```bash
    git clone [repository_url]
    cd PetPal
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv venv
    venv\Scripts\activate   # On Windows
    source venv/bin/activate  # On macOS and Linux
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**

    -   Create a `.env` file in the root directory.
    -   Add the following variables:

        ```properties
        FLASK_SECRET_KEY=your-secret-key
        OPENROUTER_API_KEY=your-openrouter-api-key
        DATABASE_URL=postgresql://petpal_user:deepu123@localhost:5432/petpal
        ```

    -   Replace `your-secret-key` with a strong, random key.
    -   Replace `your-openrouter-api-key` with your OpenRouter API key (if applicable).
    -   Configure the `DATABASE_URL` to match your PostgreSQL setup.

5.  **Initialize the database:**

    ```bash
    # Ensure PostgreSQL server is running
    # Create the database if it doesn't exist
    # Run the Flask application to create tables
    python app.py
    ```

6.  **Run the application:**

    ```bash
    flask run
    ```

    or

    ```bash
    python app.py
    ```

## Usage

-   Register a new account or log in with existing credentials.
-   Add your pets to the dashboard.
-   Manage health records, reminders, and tasks for each pet.
-   View care tips specific to your pet's species.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

[License]
