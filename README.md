# Vehicle Registration Growth Dashboard (Investor View)

## 📌 Overview
This project is built for the **Financially Free Backend Developer Internship** assignment.  
It provides an **investor-focused dashboard** showing **Year-over-Year (YoY)** and **Quarter-over-Quarter (QoQ)** growth for vehicle registrations in India, broken down by **vehicle category (2W, 3W, 4W)** and **manufacturer**.  
Data is sourced from the **Vahan Dashboard**.

---

## 🚀 Features
- **Multiple Categories:** 2W, 3W, and 4W manufacturer-wise data
- **Filters:** Date range, vehicle category, manufacturer selection
- **Interactive Charts:**
  - Monthly trends by category & manufacturer
  - QoQ % and YoY % growth bars
- **Key Metrics:** Latest month total, QoQ %, YoY %, latest quarter
- **Auto-Generated Investor Insights:**
  - Highlights best/worst performing categories
  - Flags top manufacturers with highest growth/decline
  - Notes structural growth vs. short-term momentum
- **Smart Display:** Hides YoY/QoQ metrics if insufficient history

---

## 📊 Data Source
**Vahan Dashboard:** [https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml](https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml)  

Collected monthly manufacturer-wise registration data for:
- **2W:** 2023, 2024, 2025
- **3W:** 2023, 2024, 2025
- **4W:** 2023, 2024, 2025

---

## 🛠️ Tech Stack
- **Backend & Processing:** Python, Pandas, NumPy
- **Frontend:** Streamlit, Plotly
- **Data Handling:** Modular normalization scripts for Vahan exports
- **Version Control:** Git/GitHub

---
--------------------------------------------------------------------------------------------------------

## 📂 Project Structure
financially-free-vehicles/
├── app.py # Streamlit dashboard
├── utils/
│ └── transforms.py # Data normalization & growth calculation
├── data/
│ └── vahan_master_full.csv # Combined cleaned dataset (2023–2025)
├── requirements.txt
└── README.md

--------------------------------------------------------------------------------------------------------

## ⚙️ Setup Instructions

1. **Clone the repo**
```bash
git clone <your-repo-url>
cd financially-free-vehicles

2. **Install dependencies**

pip install -r requirements.txt

3. **Run the app**

streamlit run app.py

4. **Open in browser**

Default: http://localhost:8501

--------------------------------------------------------------------------------------------------------

📈 How to Use
Adjust date range and filters from the sidebar

Explore:

Key Metrics → Quick investor snapshot

Category Trends → Monthly trends & growth bars

Manufacturer View → Top OEMs by size and growth

Read Investor Insights (Auto) at the bottom for ready-to-use commentary

--------------------------------------------------------------------------------------------------------

📌 Data Assumptions
Vahan data is assumed accurate for months exported

Missing months are excluded from growth calculations

QoQ and YoY require at least 2 and 5 quarters of data respectively to display

--------------------------------------------------------------------------------------------------------

📍 Feature Roadmap (If Continued)
Automate monthly scraping from Vahan Dashboard

Integrate state-wise breakdown

Include market share trends for top OEMs

Add export options (PDF, Excel) for investor reports

--------------------------------------------------------------------------------------------------------

🎯 Bonus Insight (from latest data)
2W category saw -39.6% QoQ decline in 2025Q1

3W remained flat at 0% QoQ — resilient short-term momentum

4W category dropped -35.6% QoQ, led by declines in TVS Motor Company Ltd

Total market QoQ change: -26.4% in 2025Q1

--------------------------------------------------------------------------------------------------------

📹 Video Walkthrough
Link: (Google Drive link here)

This video demonstrates:
Setting filters
Navigating the dashboard
Reading auto-generated investor insights
Key conclusions from the data
