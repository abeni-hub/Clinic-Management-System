# 🏥 Clinic Management System  

This is an **Advanced Clinic Management System** built to handle **end-to-end clinical workflows**.  
It provides a centralized system to manage patients, staff, appointments, lab tests, and billing.  

The project is divided into:  
- **Backend:** Django REST Framework (my contribution ✅)  
- **Frontend:** React  

---

## 🔎 Description  

- I developed the **entire backend** using **Django REST Framework**.  
- Implemented **JWT Authentication** for secure login and API access.  
- Built a **Role-Based Access Control (RBAC)** system to manage different user types:  
  - **Admin** 👑 → Full system access and user management  
  - **Reception** 📝 → Patient registration & appointment scheduling  
  - **Doctor** ⚕️ → View patient history & consultations  
  - **Nurse** 👩‍⚕️ → Assist doctors and update patient vitals  
  - **Laboratorist** 🔬 → Manage lab tests and results  
  - **Injection Room** 💉 → Record administered injections & treatments  

- The frontend (React) consumes the API endpoints for a seamless user experience.  
- The project is **deployed on shared hosting**, making it accessible online.  

---

## ⚙️ Features  

- ✅ **JWT Authentication** for secure API access  
- ✅ **Role-based user permissions** (Admin, Reception, Doctor, Nurse, Lab, Injection Room)  
- ✅ **Patient Management** (register, update, history tracking)  
- ✅ **Appointment Scheduling**  
- ✅ **Consultations & Medical Records**  
- ✅ **Laboratory Test Management**  
- ✅ **Injection & Treatment Tracking**  
- ✅ **Billing & Reports**  
- ✅ **Deployed on Shared Hosting** for real-world accessibility  

---

## 🛠️ Tech Stack  

- **Backend:** Django REST Framework (DRF)  
- **Authentication:** JWT (JSON Web Token)  
- **Frontend:** React  
- **Database:** PostgreSQL / MySQL (depending on deployment)  
- **Hosting:** Shared Hosting Deployment  

---

## 🚀 Installation & Setup  

### 1. Clone the Repository  
```bash
git clone <REPO_URL>
cd clinic-management-system
```
### 2. Backend Setup (Django REST Framework)
```bash
cd backend
python -m venv venv
source venv/bin/activate   # For Linux/Mac
venv\Scripts\activate      # For Windows

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Backend runs at: http://127.0.0.1:8000

**🔐 Authentication (JWT)**

Users log in with credentials and receive a JWT token.

The token must be included in the Authorization header for API requests:
```bash
Authorization: Bearer <your_token>
```
**🖼️ System Architecture**

flowchart TD

    A[Frontend - React] --> B[Django REST API]
    B --> C[JWT Authentication]
    B --> D[Role-Based Access Control]
    B --> E[Database\nSqlite\Postgres]
    
    subgraph Roles
        F[Admin]
        G[Reception]
        H[Doctor]
        I[Nurse]
        J[Laboratorist]
        K[Injection Room]
    end
    
    B --> Roles

**📬 Contact**

LinkedIn: Abenezer Sileshi

Gmail: abinesilew@gmail.com

Telegram: @Aben14i
