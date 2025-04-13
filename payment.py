import stripe
import os

# Set your Stripe secret key using environment variables for production
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def process_payment(user, amount, description="", stripe_token=None):
    try:
        # Create a PaymentIntent using Stripe's API
        charge = stripe.Charge.create(
            amount=int(amount * 100),  # Amount in pence/cents
            currency='gbp',
            description=description,
            source=stripe_token,
            metadata={"user_id": user.id}
        )
        print(f"Processed payment for {user.email}: £{amount} for {description}")
        return True
    except stripe.error.CardError as e:
        print(f"Card error: {e.user_message}")
        return False
    except stripe.error.RateLimitError as e:
        print(f"Rate limit error: {e.user_message}")
        return False
    except stripe.error.InvalidRequestError as e:
        print(f"Invalid request error: {e.user_message}")
        return False
    except stripe.error.AuthenticationError as e:
        print(f"Authentication error: {e.user_message}")
        return False
    except stripe.error.APIConnectionError as e:
        print(f"API connection error: {e.user_message}")
        return False
    except stripe.error.StripeError as e:
        print(f"Stripe error: {e.user_message}")
        return False
    except Exception as e:
        print(f"Payment error: {e}")
        return False
