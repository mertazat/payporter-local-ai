class PaymentService:

    def create_transfer(self, sender_id, receiver_id, amount):
        if amount <= 0:
            raise ValueError("Transfer amount must be greater than zero")

        if sender_id == receiver_id:
            raise ValueError("Sender and receiver cannot be the same")

        return {
            "status": "success",
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "amount": amount
        }

    def increase_credit_limit(self, user, requested_limit):
        current_limit = user["credit_limit"]

        if requested_limit <= current_limit:
            raise ValueError("New limit must be greater than current limit")

        if requested_limit > 100000:
            raise ValueError("Maximum credit limit is 100000")

        user["credit_limit"] = requested_limit

        return {
            "status": "approved",
            "new_limit": requested_limit
        }
