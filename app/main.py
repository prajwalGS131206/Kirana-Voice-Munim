
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.database.init_db import initialize_database
from app.database.operations import (
    get_customers,
    add_customer,
    add_transaction,
    get_customer_balance,
    find_customer_by_name,
    get_customer_transactions
)
from app.services.transaction_parser import parse_transaction

app = FastAPI(
    title="Kirana Voice Munim",
    description="A Voice-Based Digital Khata for Kirana Stores",
    version="1.0.0"
)


class CustomerCreate(BaseModel):
    name: str
    phone: Optional[str] = None


class TransactionCreate(BaseModel):
    customer_id: int
    transaction_type: str
    amount: float
    note: Optional[str] = None


class VoiceTransactionCreate(BaseModel):
    transcript: str


@app.on_event("startup")
def startup():
    initialize_database()


@app.get("/")
def home():
    return {
        "success": True,
        "message": "Kirana Voice Munim API is running!"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/customers")
def customers():
    return {
        "success": True,
        "customers": [dict(customer) for customer in get_customers()]
    }


@app.post("/customers")
def create_customer(customer: CustomerCreate):
    try:
        customer_id = add_customer(customer.name, customer.phone)

        return {
            "success": True,
            "message": "Customer added successfully",
            "customer_id": customer_id,
            "name": customer.name
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/transactions")
def create_transaction(transaction: TransactionCreate):
    customers = get_customers()

    if not any(
        customer["id"] == transaction.customer_id
        for customer in customers
    ):
        raise HTTPException(status_code=404, detail="Customer not found")

    try:
        transaction_id = add_transaction(
            transaction.customer_id,
            transaction.transaction_type,
            transaction.amount,
            transaction.note
        )

        balance = get_customer_balance(transaction.customer_id)

        return {
            "success": True,
            "message": "Transaction saved successfully",
            "transaction_id": transaction_id,
            "balance": balance
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/transactions/voice")
def create_voice_transaction(data: VoiceTransactionCreate):
    parsed = parse_transaction(data.transcript)

    if not parsed.get("success"):
        raise HTTPException(
            status_code=400,
            detail=parsed.get("error", "Could not understand transaction")
        )

    customer_name = parsed["customer_name"]
    transaction_type = parsed["transaction_type"]
    amount = parsed["amount"]

    matches = find_customer_by_name(customer_name)

    if not matches:
        raise HTTPException(
            status_code=404,
            detail="Customer name not found."
        )

    if len(matches) > 1:
        raise HTTPException(
            status_code=400,
            detail="Multiple customers found. Please use a more specific name."
        )

    customer = matches[0]

    try:
        transaction_id = add_transaction(
            customer["id"],
            transaction_type,
            amount,
            data.transcript
        )

        balance = get_customer_balance(customer["id"])

        return {
            "success": True,
            "message": "Voice transaction saved successfully",
            "customer_name": customer["name"],
            "spoken_name": customer_name,
            "transaction_type": transaction_type,
            "amount": amount,
            "balance": balance,
            "transaction_id": transaction_id
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/customers/{customer_id}/balance")
def customer_balance(customer_id: int):
    customers = get_customers()

    if not any(customer["id"] == customer_id for customer in customers):
        raise HTTPException(status_code=404, detail="Customer not found")

    return {
        "success": True,
        "customer_id": customer_id,
        "balance": get_customer_balance(customer_id)
    }


@app.get("/customers/{customer_id}/transactions")
def customer_transaction_history(customer_id: int):
    customers = get_customers()

    if not any(customer["id"] == customer_id for customer in customers):
        raise HTTPException(status_code=404, detail="Customer not found")

    transactions = get_customer_transactions(customer_id)

    return {
        "success": True,
        "customer_id": customer_id,
        "transactions": [dict(transaction) for transaction in transactions]
    }
