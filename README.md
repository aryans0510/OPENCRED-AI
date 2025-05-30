# 🧠 OpenCredAI – Inclusive Credit & Home Loan Recommender

Welcome to **OpenCredAI**, an AI-powered web app that generates inclusive credit scores and recommends fair home loans for financially invisible users using alternative data. Built for hackathons, social impact, and ethical fintech innovation.

---

## 🚀 Features

- 📱 **Minimal Input**: Just income and occupation type
- 🤖 **Alt-Data Civil Score**: Simulated score using mobile usage, location stability, and UPI activity
- 🏦 **Loan Recommendations**: Get the most suitable home loan offers with EMI breakdown
- 💬 **GPT-Powered Explanation**: Natural language reasons for the loan recommendation
- 📄 **Downloadable PDF Report**: Summary with score, logic, loan info, and insights

---

## 🔧 Tech Stack

| Component          | Technology                  |
|-------------------|-----------------------------|
| Frontend/UI       | Streamlit                   |
| Credit Model      | Python + heuristics + NumPy |
| Alt-Data Simulator| NumPy                       |
| AI Explanation    | OpenAI GPT API              |
| PDF Generator     | FPDF                        |
| WhatsApp Bot (*)  | Flask + Twilio              |

(*) WhatsApp integration is optional and comes with a separate backend.

---

## ▶️ How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/aryans0510/OPENCRED-AI
cd OpenCredAI
```

### 2. Install Dependencies
```bash
pip install streamlit numpy pandas openai fpdf flask twilio
```

### 3. Set OpenAI Key
Create a `.streamlit/secrets.toml` file:
```toml
OPENAI_API_KEY = "your-openai-key"
```

### 4. Run the Streamlit App
```bash
streamlit run opencredai_app.py
```

---

## 🧪 Simulated Data Logic
The app simulates alternative credit signals like:
- **Location stability**: Mocked float from 0–1
- **Mobile usage score**: Random score out of 100
- **UPI transaction count**: Simulated number of digital transactions

These feed into a heuristic civil score between 300 and 900.

---

## 🌐 WhatsApp UI (Optional)
Want to run OpenCredAI as a WhatsApp bot?
1. Set up a Twilio Sandbox for WhatsApp
2. Run `flask_app.py`
3. Use `ngrok` to tunnel local server
```bash
ngrok http 5000
```
4. Add the webhook URL to Twilio console

---

## 📂 Project Structure
```
├── opencredai_app.py         # Streamlit frontend
├── flask_app.py              # WhatsApp backend (optional)
├── requirements.txt          # Python dependencies
├── .streamlit/secrets.toml   # API keys
├── README.md                 # This file
```

---

## 🌍 Impact Goals
- 💠 Aligned with **UN SDGs**: No Poverty, Reduced Inequalities
- 🔍 Inclusive FinTech: Serving thin-file/no-file users
- 🧠 Explainable AI: Building trust with human-readable logic

---

## 📩 Contact / Collaboration
- Author:ARYAN SINGH
- Email: aryands0510@gmail.com
- Hackathon Team: Team Anchor


