// Initialize Stripe
const stripe = Stripe(window.paymentConfig.stripePublicKey);
const elements = stripe.elements();

// Create card Element and mount it
const card = elements.create('card', {
    style: {
        base: {
            fontSize: '16px',
            color: '#424770',
            '::placeholder': { color: '#aab7c4' }
        },
        invalid: { color: '#9e2146' }
    }
});
card.mount('#card-element');

// Handle payment method selection
const paymentMethods = document.querySelectorAll('input[name="payment_method"]');
const paymentForms = {
    stripe: document.getElementById('stripe-form'),
    paypal: document.getElementById('paypal-form'),
    apple_pay: document.getElementById('apple-pay-form'),
    google_pay: document.getElementById('google-pay-form')
};

paymentMethods.forEach(method => {
    method.addEventListener('change', (e) => {
        Object.values(paymentForms).forEach(form => form.classList.add('d-none'));
        paymentForms[e.target.value].classList.remove('d-none');
    });
});

// Handle Stripe payment
const form = document.getElementById('payment-form');
form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const submitButton = document.getElementById('submit-button');
    const spinner = document.getElementById('spinner');
    const buttonText = document.getElementById('button-text');

    submitButton.disabled = true;
    spinner.classList.remove('d-none');
    buttonText.textContent = 'Processing...';

    try {
        const { paymentMethod, error } = await stripe.createPaymentMethod({
            type: 'card',
            card: card
        });

        if (error) {
            const errorElement = document.getElementById('card-errors');
            errorElement.textContent = error.message;
            submitButton.disabled = false;
            spinner.classList.add('d-none');
            buttonText.textContent = 'Pay Now';
        } else {
            const response = await fetch(`${window.paymentConfig.apiUrl}create/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    order_id: window.paymentConfig.orderId,
                    payment_method: 'stripe',
                    payment_method_id: paymentMethod.id
                })
            });

            const data = await response.json();
            if (response.ok) {
                window.location.href = window.paymentConfig.successUrl;
            } else {
                throw new Error(data.error);
            }
        }
    } catch (error) {
        window.location.href = `${window.paymentConfig.failureUrl}?error=${encodeURIComponent(error.message)}`;
    }
});

// Initialize PayPal
paypal.Buttons({
    createOrder: async () => {
        try {
            const response = await fetch(`${window.paymentConfig.apiUrl}create/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    order_id: window.paymentConfig.orderId,
                    payment_method: 'paypal'
                })
            });
            const data = await response.json();
            return data.paypal_order_id;
        } catch (error) {
            console.error('Error:', error);
        }
    },
    onApprove: async (data) => {
        try {
            const response = await fetch(`${window.paymentConfig.apiUrl}verify-paypal/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    order_id: window.paymentConfig.orderId,
                    paypal_order_id: data.orderID
                })
            });
            if (response.ok) {
                window.location.href = window.paymentConfig.successUrl;
            } else {
                const errorData = await response.json();
                window.location.href = `${window.paymentConfig.failureUrl}?error=${encodeURIComponent(errorData.error)}`;
            }
        } catch (error) {
            window.location.href = `${window.paymentConfig.failureUrl}?error=${encodeURIComponent(error.message)}`;
        }
    }
}).render('#paypal-button-container');

// Initialize Apple Pay
if (window.ApplePaySession && ApplePaySession.canMakePayments()) {
    const applePayButton = document.getElementById('apple-pay-button');
    applePayButton.addEventListener('click', async () => {
        try {
            const response = await fetch(`${window.paymentConfig.apiUrl}create/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    order_id: window.paymentConfig.orderId,
                    payment_method: 'apple_pay'
                })
            });
            const data = await response.json();
            
            const paymentRequest = stripe.paymentRequest({
                country: 'US',
                currency: 'usd',
                total: {
                    label: 'Order Payment',
                    amount: window.paymentConfig.amount * 100,
                },
                requestPayerName: true,
                requestPayerEmail: true,
                requestPayerPhone: true,
            });

            const pr = paymentRequest.createPaymentMethod();
            pr.on('paymentmethod', async (e) => {
                try {
                    const { paymentMethod, error } = await stripe.confirmCardPayment(
                        data.client_secret,
                        { payment_method: e.paymentMethod.id }
                    );
                    if (error) {
                        e.complete('fail');
                        window.location.href = `${window.paymentConfig.failureUrl}?error=${encodeURIComponent(error.message)}`;
                    } else {
                        e.complete('success');
                        window.location.href = window.paymentConfig.successUrl;
                    }
                } catch (error) {
                    e.complete('fail');
                }
            });
        } catch (error) {
            console.error('Error:', error);
        }
    });
} else {
    document.getElementById('apple-pay-button').style.display = 'none';
}

// Initialize Google Pay
const googlePayButton = document.getElementById('google-pay-button');
googlePayButton.addEventListener('click', async () => {
    try {
        const response = await fetch(`${window.paymentConfig.apiUrl}create/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({
                order_id: window.paymentConfig.orderId,
                payment_method: 'google_pay'
            })
        });
        const data = await response.json();
        
        const paymentRequest = stripe.paymentRequest({
            country: 'US',
            currency: 'usd',
            total: {
                label: 'Order Payment',
                amount: window.paymentConfig.amount * 100,
            },
            requestPayerName: true,
            requestPayerEmail: true,
            requestPayerPhone: true,
        });

        const pr = paymentRequest.createPaymentMethod();
        pr.on('paymentmethod', async (e) => {
            try {
                const { paymentMethod, error } = await stripe.confirmCardPayment(
                    data.client_secret,
                    { payment_method: e.paymentMethod.id }
                );
                if (error) {
                    e.complete('fail');
                    window.location.href = `${window.paymentConfig.failureUrl}?error=${encodeURIComponent(error.message)}`;
                } else {
                    e.complete('success');
                    window.location.href = window.paymentConfig.successUrl;
                }
            } catch (error) {
                e.complete('fail');
            }
        });
    } catch (error) {
        console.error('Error:', error);
    }
}); 