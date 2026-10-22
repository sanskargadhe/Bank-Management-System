# Bank Management System

A web-based Bank Management System developed using Python, Streamlit, and PostgreSQL. This project provides a user-friendly interface for managing bank accounts, performing basic banking transactions, and maintaining transaction audit logs.

## Features

- **Account Creation:** Create a new bank account with a generated account number and 4-digit PIN.
- **Customer Login:** Log in using an account number and PIN.
- **Dashboard:** View account details and current balance.
- **Deposit Money:** Deposit money with amount validation.
- **Withdraw Money:** Withdraw money while checking the available balance.
- **Transaction History:** View account-specific activity and audit logs.
- **Account Management:** Update account name and PIN or delete an account with confirmation.
- **Admin Panel:** View and clear audit logs.
- **Database Integration:** Store account information and audit records in PostgreSQL.
- **Environment Variables:** Keep database credentials and admin passwords outside the source code.

## Technologies Used

- Python
- Streamlit
- PostgreSQL
- Psycopg2
- python-dotenv
- Pandas (if used by the application)

## Project Structure

```text
Bank-Management-System/
├── app.py
├── main2.py
├── Database.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Bank-Management-System
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your repository URL.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the environment variables

Create a local file named `.env` in the project root using `.env.example` as a template.

Set the following variables with your own values:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=BankData
DB_USER=postgres
DB_PASSWORD=your_postgresql_password
BANK_ADMIN_PASSWORD=your_admin_password
```

Never upload your actual `.env` file or real credentials to GitHub.

### 5. Configure PostgreSQL

Install and start PostgreSQL. Create a database named `BankData` and ensure the database user has the required permissions.

The application must be able to connect to the configured database.

### 6. Run the application

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal, usually:

`http://localhost:8501`

## Security Considerations

This project is intended for educational purposes and is not suitable for real banking transactions. A production system would require secure PIN hashing, stronger authentication, authorization controls, robust transaction handling, and additional security testing.

## Future Improvements

- Improve authentication and account security.
- Add transaction filtering and reporting.
- Introduce more detailed financial analytics.
- Deploy the application with a hosted PostgreSQL database.
- Improve automated testing and error handling.

## Author

Sanskar Gadhe