class PaymentService:

    def transfer_money(self, sender_id, receiver_id, amount):
        if amount <= 0:
            raise ValueError("Transfer amount must be greater than zero")

        if sender_id == receiver_id:
            raise ValueError("Sender and receiver cannot be the same")

        transaction = {
            "sender": sender_id,
            "receiver": receiver_id,
            "amount": amount,
            "status": "COMPLETED"
        }

        return transaction

    def cancel_transfer(self, transaction):
        if transaction["status"] == "COMPLETED":
            transaction["status"] = "CANCELLED"

        return transaction

