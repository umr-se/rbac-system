# 🔒 RBAC System - Role-Based Access Control System 🔐

This backend system is built with **FastAPI** ⚡ and **MySQL** 🗄️, providing secure authentication & authorization via **JWT** 🔑. It ensures structured access control with two user roles:

## 👤 User:
- ✅ Can create an account and manage their own details
- ✅ Create & view events, plus download ICS files 📅

## 🛠️ Admin:
- ✅ Has full control to create, update, delete, and manage users
- ✅ Promote users to admins and manage all events 📊

## 🔄 Authentication & Authorization Workflow:
- 🔹 Users must authenticate first
- 🔹 A JWT token is generated for secure access
- 🔹 Admins get elevated privileges to manage users & events

## 🚢 Deployment & Monitoring:
- 📦 **Deployed on Docker** 🐳
- 📊 **Real-time monitoring** with **Prometheus + Grafana** for logging & request analysis

## 🛠️ Setup & Installation:
### Prerequisites:
- **Python 3.9+** is required
- Install **venv** (Virtual Environment):
  ```sh
  python -m venv venv
  source venv/bin/activate  # On macOS/Linux
  venv\Scripts\activate  # On Windows
  ```
- Install dependencies from `requirements.txt`:
  ```sh
  pip install -r requirements.txt
  ```
- Run Docker Compose to set up services:
  ```sh
  docker-compose up --build
  ```

![img1](https://github.com/user-attachments/assets/c2f59be6-9e29-434f-9a77-b625e00407a3)
![img2](https://github.com/user-attachments/assets/305140a7-8a7e-447d-b124-dc355d667e78)
![img3](https://github.com/user-attachments/assets/f8430a5c-bdc4-4fe1-a690-a5c2bb110a6c)
![img4](https://github.com/user-attachments/assets/2cee8c29-f592-46a0-96de-610059e4fb88)


This project ensures a **scalable, secure, and well-monitored** access control system, perfect for enterprise applications! 🚀
