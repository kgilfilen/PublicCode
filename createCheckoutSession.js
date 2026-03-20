// netlify/functions/createCheckoutSession.js
// Uses Stripe API to create customer checkout
const Stripe = require("stripe");
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

const stripe_price_id = "price_1SkqRQLy6kZvGQwFi3YdUYye";
const my_site_url = "https://www.meetwomenbetter.org";
const API_KEY = process.env.CHECKOUT_API_KEY;

// Simple in-memory rate limiter
const RATE_LIMIT = {};
const WINDOW_MS = 60000; // 1 minute
const MAX_REQUESTS_PER_WINDOW = 5;

exports.handler = async function (event) {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method Not Allowed" };
  }

  // Checks API key header, my local simple security
  const clientKey = event.headers["x-api-key"];
  if (clientKey !== API_KEY) {
    return { statusCode: 401, body: "Unauthorized" };
  }

  // Rate limiting by IP, reduces Somalian bots hitting Stripe
  const ip = event.headers["client-ip"] || event.headers["x-forwarded-for"] || "unknown";
  if (!RATE_LIMIT[ip]) {
    RATE_LIMIT[ip] = { count: 0, start: Date.now() };
  }

  const elapsed = Date.now() - RATE_LIMIT[ip].start;
  if (elapsed > WINDOW_MS) {
    RATE_LIMIT[ip] = { count: 0, start: Date.now() };
  }

  RATE_LIMIT[ip].count++;
  if (RATE_LIMIT[ip].count > MAX_REQUESTS_PER_WINDOW) {
    return { statusCode: 429, body: "Too many requests" };
  }

  try {
    // Parses the request body
    const { variant } = JSON.parse(event.body);

    // Creates Stripe Checkout session
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ["card"],
      mode: "subscription",
      payment_method_collection: "always",
      line_items: [
        { price: stripe_price_id, quantity: 1 }
      ],
      subscription_data: {
        trial_period_days: 30,
        metadata: { variant },
      },
      success_url: `${my_site_url}/thank-you?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${my_site_url}/variant-redirect?fromStripe=true`
    });

    return {
      statusCode: 200,
      body: JSON.stringify({ url: session.url })
    };
  } catch (err) {
    console.error(err);
    return { statusCode: 500, body: "Server error creating session" };
  }
};
