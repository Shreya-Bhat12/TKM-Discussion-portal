# 🚗 QAC Discussion Portal

A full-stack web application designed to manage **part-related discussions, shipments, and issue tracking** across departments like QAC, QIC, Production, Dealers, and Suppliers.

---

## 📌 Overview

The QAC Discussion Portal helps teams:

* Track defective or problematic parts
* Manage shipment records
* Collaborate through structured discussions
* Monitor status and lead times
* View cumulative insights across all parts

---

## ⚙️ Tech Stack

* **Backend:** Python (Flask)
* **Database:** PostgreSQL
* **Frontend:** HTML, CSS, JavaScript
* **Visualization Integration:** Power BI

---

## ✨ Key Features

### 🔐 Authentication System

* Admin and Dealer login
* Role-based access (QAC, QIC, Production, Dealer, etc.)

### 📦 Shipment Management

* Add, edit, delete shipments
* Track:

  * Part Name & Number
  * Model
  * Supplier
  * Customer Concern
  * PI Number
  * Status & Remarks

### 💬 Discussion System

* Each shipment has a dedicated discussion thread
* Department-wise communication
* Edit and track message history

### 📊 Dashboards

#### 1. Normal Dashboard

* Tabular view of all shipments
* Filters:

  * Model
  * Supplier
  * Status
  * Category
  * Date
* Pagination support

#### 2. Summary Dashboard

* Grouped by Part Name + Model
* Shows:

  * Total cases
  * Status breakdown
  * Lead time tracking
* Expandable rows for detailed view

### 📈 Cumulative Discussions

* View **all discussions across all parts**
* Expand individual part discussions inline
* Message count tracking

### ⏱️ Lead Time Tracking

* Automatic 3-day lead time calculation
* Visual indicators:

  * ✅ Within time
  * ⚠️ Lead time crossed

### 🗑️ Trash / Closed OFP

* Soft delete shipments
* Restore or permanently delete (admin only)

### 📊 Power BI Integration

* Quick access to external reports via dashboard button

---

## 🗄️ Database Schema

### Tables:

* `admins` → Admin users
* `dealers` → Registered users
* `shipments` → Part/shipment records
* `Discussion` → Messages linked to shipments

---

## 🚀 Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-username/qac-discussion-portal.git
cd qac-discussion-portal
```

### 2. Install Dependencies

```bash
pip install flask psycopg2
```

### 3. Configure Database

Update credentials in:

```python
def get_db():
    psycopg2.connect(
        host="localhost",
        database="postgres",
        user="YOUR_USER",
        password="YOUR_PASSWORD",
        port="5432"
    )
```

### 4. Initialize Database

Run the app once to auto-create tables:

```bash
python app.py
```

### 5. Run Application

```bash
python app.py
```

Open in browser:

```
http://127.0.0.1:5000/
```

---

## 🔑 Default Admin Credentials

| Role             | Username  | Password |
| ---------------- | --------- | -------- |
| QAC Admin        | qacadmin  | qac123   |
| QIC Admin        | qicadmin  | qic123   |
| Production Admin | prodadmin | prod123  |

---

## 📂 Project Structure

```
├── app.py
├── templates (inline rendering used)
├── static (CSS/JS if separated)
├── database (PostgreSQL)
└── README.md
```

---

## 📌 Future Enhancements

* AI-based issue prediction
* Real-time notifications
* Email alerts for lead time breaches
* Advanced analytics dashboard
* File/image attachments in discussions

## 🤝 Contribution

Contributions are welcome!

1. Fork the repo
2. Create a feature branch
3. Commit changes
4. Submit a pull request


## 📄 License

This project is for educational and internal use. You can modify and extend as needed.

* Create **API documentation**
* Improve this into a **resume-level project description** 🚀
