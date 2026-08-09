import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = 'http://shopflow-alb-218604079.eu-west-1.elb.amazonaws.com';

export const options = {
  scenarios: {
    ramp_up: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [{ duration: '5m', target: 50 }],
      gracefulRampDown: '30s',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<2000'],
    http_req_failed: ['rate<0.05'],
  },
};

export default function () {
  const email = `loadtest_${__VU}_${__ITER}_${Date.now()}@example.com`;
  const password = 'LoadTest123!';

  const registerRes = http.post(
    `${BASE_URL}/api/users/register`,
    JSON.stringify({ email, password }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  check(registerRes, { 'register succeeded': (r) => r.status === 201 });

  const loginRes = http.post(
    `${BASE_URL}/api/users/login`,
    JSON.stringify({ email, password }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  check(loginRes, { 'login succeeded': (r) => r.status === 200 });

  const token = loginRes.json('access_token');
  if (!token) {
    sleep(1);
    return;
  }
  const authHeaders = {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
  };

  const createProductRes = http.post(
    `${BASE_URL}/api/products/`,
    JSON.stringify({
      name: `Load Test Product ${__VU}-${__ITER}`,
      price: 9.99,
      stock: 100,
    }),
    authHeaders
  );
  check(createProductRes, { 'product created': (r) => r.status === 201 });

  const productId = createProductRes.json('id');
  if (!productId) {
    sleep(1);
    return;
  }

  const addToCartRes = http.post(
    `${BASE_URL}/api/cart/items`,
    JSON.stringify({ product_id: productId, quantity: 2 }),
    authHeaders
  );
  check(addToCartRes, { 'added to cart': (r) => r.status === 200 });

  const placeOrderRes = http.post(
    `${BASE_URL}/api/orders/`,
    JSON.stringify({
      items: [{ product_id: productId, quantity: 2, unit_price: 9.99 }],
    }),
    authHeaders
  );
  check(placeOrderRes, { 'order placed': (r) => r.status === 201 });

  sleep(1);
}
