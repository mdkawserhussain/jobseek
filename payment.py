import stripe
import os

# Set your Stripe secret key using environment variables for production
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Function to process payment using Stripe

def process_payment(user, amount, description=""):
    try:
        # Create a PaymentIntent using Stripe's API
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Amount in pence/cents
            currency='gbp',
            metadata={"user_id": user.id, "description": description}
        )
        print(f"Processed payment for {user.email}: £{amount} for {description}")
        return True
    except stripe.error.CardError as e:
        # Handle card errors
        print(f"Card error: {e.user_message}")
        return False
    except stripe.error.RateLimitError as e:
        # Handle rate limit errors
        print(f"Rate limit error: {e.user_message}")
        return False
    except stripe.error.InvalidRequestError as e:
        # Handle invalid requests
        print(f"Invalid request error: {e.user_message}")
        return False
    except stripe.error.AuthenticationError as e:
        # Handle authentication errors
        print(f"Authentication error: {e.user_message}")
        return False
    except stripe.error.APIConnectionError as e:
        # Handle API connection errors
        print(f"API connection error: {e.user_message}")
        return False
    except stripe.error.StripeError as e:
        # Handle generic Stripe errors
        print(f"Stripe error: {e.user_message}")
        return False
    except Exception as e:
        # Handle other exceptions
        print(f"Payment error: {e}")
        return False
