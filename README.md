# BUS TICKET BOOKING

## Overview
Bus Ticket Booking is a web application built using Flask and SQLite, designed to streamline the bus ticket reservation process. This project utilizes Object-Oriented Programming principles to ensure a structured and maintainable codebase.

## Features
- **Admin Capabilities**:
  - Add and remove bus routes.
  - Set and update costs for each route.
  - Manage seat allocations and availability.

- **User Features**:
  - Browse available bus routes and their details.
  - Book and cancel seat reservations, with real-time updates for all users.
  - Secure login and signup functionality with password hashing using `werkzeug.security` for enhanced security.

## Installation

To install and run the project, follow these steps:

1. Clone the repository:
   in bash
   git clone <repository-url>
   
2. Navigate into the project directory:
   cd <project-directory>
   
3. Run the application:
   python app.py

## Technologies Used
Programming Languages: Python, HTML, CSS, JavaScript
Framework: Flask
Database: SQLite
Key Libraries:
werkzeug.security for password hashing.
Database:
The project includes an SQLite database that supports all CRUD operations, allowing efficient management of user data, bus routes, and bookings.

## Authors
This project was developed by:

Mayuresh Sawant<br>
Hasnain Khan<br>
Ghanshyam Kumavat<br>
As college students, we collaborated to create this project as part of our coursework. We hope this application makes the bus booking process more efficient and user-friendly.
