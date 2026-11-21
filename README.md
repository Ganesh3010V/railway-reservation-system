# Railway Reservation System with Multi-Leg Journey Support and Automated Waitlist Management

A full-featured Railway Reservation System DBMS project built with Flask and MySQL.

## Features
- **Multi-Leg Journey Booking**: Support for multi-segment route planning and reservations.
- **Automated Waitlist Management**: Automated status updates from waitlist to confirmed upon cancellations.
- **Comprehensive Database Schema**: Features JOINs, Triggers, Stored Procedures, Foreign Keys, CHECK constraints, Aggregates, and Subqueries.
- **Web Interface**: Interactive frontend built with Flask and Bootstrap/HTML templates.
- **Reporting & Analytics**: Comprehensive query examples and automated documentation reporting tools.

## Tech Stack
- **Backend**: Python (Flask)
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap

## Setup & Running
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd "RAILWAY RESERVATION SYSTEM WITH MULTI-LEG JOURNEY SUPPORT AND AUTOMATED WAITLIST MANAGEMENT"
   ```

2. **Configure Database**:
   - Ensure MySQL server is running.
   - Import the database schema from `Railway_DBMS_Full_Schema.sql`.
   - Optionally populate sample data using `railway/demo_sample_data.sql`.

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   # or install flask mysql-connector-python
   pip install flask mysql-connector-python
   ```

4. **Start the Application**:
   - Run `start_website.bat` or:
   ```bash
   cd railway
   python app.py
   ```
   - Open your browser at `http://localhost:5000`
