import stripe

# Set your Stripe secret key (use environment variables in production)
stripe.api_key = "sk_test_yourkeyhere"

def process_payment(user, amount, description=""):
    try:
        # Create a PaymentIntent (or use your gateway's API)
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Amount in pence/cents
            currency='gbp',
            metadata={"user_id": user.id, "description": description}
        )
        # Assume payment is successful for this dummy integration
        print(f"Processed payment for {user.email}: £{amount} for {description}")
        return True
    except Exception as e:
        print(f"Payment error: {e}")
        return False
