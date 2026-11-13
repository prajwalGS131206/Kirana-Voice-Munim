# Kirana Voice Munim 🧾🎙️

### A Voice-Based Digital Khata for Kirana Stores

Kirana Voice Munim is a voice-enabled digital ledger designed to help small kirana store owners record customer credit and payment transactions using natural speech.

Instead of manually writing every transaction in a notebook, the shopkeeper can speak a transaction, and the system converts it into a structured ledger entry.

## 🚀 Key Features

- **Voice-based transactions:** Capture spoken customer transactions using a microphone.
- **Speech recognition:** Uses Gnani Vachana to convert speech into text.
- **Transaction parsing:** Identifies customer name, transaction type, and amount.
- **Digital Khata:** Stores transactions in an SQLite database.
- **Balance tracking:** Maintains customer balances after credit and payment entries.
- **REST API:** FastAPI endpoints for interacting with the digital ledger.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend | FastAPI |
| Speech Recognition | Gnani Vachana |
| Database | SQLite |
| API Documentation | Swagger UI |
| Audio Processing | SoundDevice, NumPy, SciPy |

## 🔄 How It Works

1. The shopkeeper speaks a transaction.
2. Gnani speech recognition converts the audio into text.
3. The transaction parser identifies the customer, amount, and transaction type.
4. The backend processes the transaction.
5. The transaction is saved in SQLite.
6. The customer's updated balance can be retrieved through the API.

### Example Voice Commands

- "Ramesh credit 500 rupees."
- "Ramesh paid 200 rupees."

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/prajwalGS131206/Kirana-Voice-Munim.git
cd Kirana-Voice-Munim
```

### 2. Create a virtual environment

```bash
python -m venv .ven