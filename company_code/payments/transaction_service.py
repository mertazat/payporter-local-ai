from datetime import datetime
import uuid


class TransactionService:
    def __init__(self):
        self.transactions = []

    def create_transaction(self, user_id, amount, currency="TRY"):
        if amount <= 0:
            return {"error": "Amount must be positive"}

        transaction = {
            "transaction_id": str(uuid.uuid4()),
            "user_id": user_id,
            "amount": amount,
            "currency": currency,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }

        self.transactions.append(transaction)

        return transaction

    def approve_transaction(self, transaction_id):
        for transaction in self.transactions:
            if transaction["transaction_id"] == transaction_id:
                transaction["status"] = "approved"
                return transaction

        return {"error": "Transaction not found"}

    def cancel_transaction(self, transaction_id):
        for transaction in self.transactions:
            if transaction["transaction_id"] == transaction_id:
                transaction["status"] = "cancelled"
                return transaction

        return {"error": "Transaction not found"}

    def get_user_transactions(self, user_id):
        return [
            transaction
            for transaction in self.transactions
            if transaction["user_id"] == user_id
        ]

    def get_transaction(self, transaction_id):
        for transaction in self.transactions:
            if transaction["transaction_id"] == transaction_id:
                return transaction

        return {"error": "Transaction not found"}
