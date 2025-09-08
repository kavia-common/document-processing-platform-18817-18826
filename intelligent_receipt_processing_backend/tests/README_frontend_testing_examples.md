# Frontend Testing Examples (React)

This backend exposes RESTful APIs at http://localhost:3001. Here are examples for testing the frontend using Jest + React Testing Library (RTL) and Cypress.

## 1) Unit/Integration tests with Jest + RTL

Example: testing a LoginForm that calls POST /auth/login.

```javascript
// LoginForm.jsx (example)
import React, { useState } from 'react';

export default function LoginForm({ onLoggedIn }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  async function handleSubmit(e) {
    e.preventDefault();
    const res = await fetch(`${process.env.REACT_APP_API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) throw new Error('Login failed');
    const data = await res.json();
    onLoggedIn(data.access_token);
  }
  return (
    <form onSubmit={handleSubmit}>
      <input placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
      <input placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
      <button type="submit">Login</button>
    </form>
  );
}
```

```javascript
// LoginForm.test.jsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import LoginForm from './LoginForm';

beforeEach(() => {
  process.env.REACT_APP_API_BASE = 'http://localhost:3001';
  global.fetch = jest.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ access_token: 'fake-token' }),
  });
});

test('logs in and returns token', async () => {
  const onLoggedIn = jest.fn();
  render(<LoginForm onLoggedIn={onLoggedIn} />);

  fireEvent.change(screen.getByPlaceholderText('Email'), { target: { value: 'user@example.com' } });
  fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'secret' } });
  fireEvent.click(screen.getByText('Login'));

  await waitFor(() => expect(onLoggedIn).toHaveBeenCalledWith('fake-token'));
  expect(global.fetch).toHaveBeenCalledWith(
    'http://localhost:3001/auth/login',
    expect.objectContaining({ method: 'POST' })
  );
});
```

## 2) E2E tests with Cypress

Example: uploading a document and verifying search flow.

```javascript
// cypress/e2e/upload_and_search.cy.js
describe('Upload and Search', () => {
  const api = 'http://localhost:3001';
  let token;

  before(() => {
    cy.request('POST', `${api}/auth/register`, {
      email: 'user@example.com',
      password: 'secret',
      name: 'User',
    }).then((resp) => {
      if (resp.status === 201) {
        token = resp.body.access_token;
      } else {
        // already exists -> login
        return cy.request('POST', `${api}/auth/login`, { email: 'user@example.com', password: 'secret' })
          .then(r => { token = r.body.access_token; });
      }
    });
  });

  it('uploads a document and finds it in search', () => {
    cy.visit('http://localhost:3000');

    // Use UI controls to upload, or directly call API for demo:
    const formData = new FormData();
    formData.append('title', 'ACME Invoice 2024');
    formData.append('file', new Blob(['Amount due $200']), 'invoice.txt');

    cy.request({
      method: 'POST',
      url: `${api}/documents`,
      headers: { authorization: `Bearer ${token}` },
      body: formData,
      failOnStatusCode: false,
    });

    cy.request({
      method: 'GET',
      url: `${api}/search?q=invoice`,
      headers: { authorization: `Bearer ${token}` },
    }).then((r) => {
      expect(r.status).to.eq(200);
      expect(r.body).to.be.an('array');
      expect(r.body.some(d => d.title.includes('ACME Invoice'))).to.eq(true);
    });
  });
});
```

Environment variables:
- REACT_APP_API_BASE=http://localhost:3001
- For CI, serve the frontend app and run cypress headless with `cypress run`.

```
# Jest
CI=true npm test -- --watchAll=false

# Cypress
npx cypress run --browser chrome --headless
```

These examples demonstrate mocking fetch for unit tests and using direct API calls in Cypress for setup/verification around the UI flow.
