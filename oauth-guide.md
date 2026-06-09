# OAuth — Complete Guide (Basic to Deep)

---

# PART 1: THE BASICS

## What Problem Does OAuth Solve?

Imagine a photo printing app wants to access your Google Photos.

### The Bad Old Way (before OAuth)
```
App: "Give me your Google username and password"
You: gives password 😨
App: now has FULL access to your Google account
     → can read email
     → can delete everything
     → can change password
     → you can never take access back ❌
```

This is dangerous. You gave away the master key.

### The OAuth Way
```
App: "Can I access just your photos?"
You: redirected to Google → login on GOOGLE (not the app)
Google: "This app wants to see your photos. Allow?"
You: click Allow
Google: gives app a LIMITED token (photos only)
App: can ONLY see photos, nothing else ✅
     → can't read email
     → can't delete account
     → you can revoke anytime ✅
```

OAuth = give limited access WITHOUT sharing your password.

---

## Real World Analogy — Hotel Key Card

```
Your house key (password):
  opens everything
  if you give it away → they control your whole house ❌

Hotel key card (OAuth token):
  opens only your room
  expires after checkout
  hotel can deactivate anytime
  you never give away your master key ✅
```

OAuth token = hotel key card. Limited, temporary, revocable.

---

# PART 2: KEY TERMINOLOGY

## The 4 Main Roles

```
1. Resource Owner    = YOU (the user who owns the data)

2. Client            = the APP wanting access
                       (photo printer app, your AI agent)

3. Authorization Server = the one who gives permission
                          (Google's login server)

4. Resource Server   = where your data lives
                       (Gmail API, Google Photos API)
```

### Example with Gmail
```
Resource Owner       = you (Abishek)
Client               = your AI agent
Authorization Server = Google login (accounts.google.com)
Resource Server      = Gmail API
```

---

## Authentication vs Authorization

People confuse these. They are different!

```
Authentication = WHO are you?
  → proving your identity
  → like showing your ID card
  → "I am Abishek"

Authorization = WHAT can you do?
  → what you're allowed to access
  → like your hotel key card permissions
  → "Abishek can access room 305 only"
```

Simple memory trick:
```
Authentication → AuthN → "N" for who (Name)
Authorization  → AuthZ → "Z" for what (allowed actions)
```

### Real Example
```
You login to Gmail:
  Authentication → Google checks your password (who you are)
  Authorization  → Google checks what you can access (your emails)
```

---

## What is a Scope?

Scope = exactly WHAT the app can access.

```
App requests these scopes:
  gmail.readonly   → can only READ emails
  gmail.send       → can send emails
  gmail.modify     → can read and modify
```

You control how much access by scopes:
```
Photo app asks:    photos.readonly  ← only see photos ✅
Photo app asks:    full.access      ← you should say NO ❌
```

### In Our Gmail MCP
```
Scopes we used:
  gmail.modify         → read and modify emails
  gmail.settings.basic → basic settings

This is why during auth Google showed:
"This app wants to read, send, delete emails"
That's the scope being requested.
```

---

## What is a Token?

Token = a string that proves you have permission.

```
token = "ya29.a0AfH6SMBxxx..."

Like a hotel key card encoded as text.
App shows this token → server gives access ✅
```

---

# PART 3: TYPES OF TOKENS

## Access Token

```
What:    used to actually access the data
Lifespan: short (usually 1 hour)
Used for: every API call

App → "here's my access token" → Gmail → returns emails ✅
```

Why short lived?
```
If stolen → only works for 1 hour → limited damage ✅
```

---

## Refresh Token

```
What:    used to get a NEW access token when old expires
Lifespan: long (days, months, or until revoked)
Used for: getting fresh access tokens

access token expires after 1 hour
        ↓
app uses refresh token
        ↓
Google gives new access token ✅
        ↓
no need to login again
```

### Flow Together
```
Login once
   ↓
get access_token (1 hour) + refresh_token (long term)
   ↓
use access_token for API calls
   ↓
after 1 hour → access_token expired
   ↓
use refresh_token → get new access_token
   ↓
continue without login ✅
```

This is why you logged in ONCE for Gmail but it keeps working.

---

## ID Token (OpenID Connect)

```
What:    contains info about WHO you are
Format:  JWT (JSON Web Token)
Contains: your name, email, profile pic

Used for: authentication (proving identity)
```

More on this in OpenID section below.

---

# PART 4: OAUTH 2.0 FLOW (Step by Step)

## The Authorization Code Flow (most common)

This is what we did with Gmail!

```
Step 1: App redirects you to Google
  "Hey Google, this app wants gmail.readonly access"
        ↓
Step 2: You login on Google + click Allow
        ↓
Step 3: Google sends back an AUTHORIZATION CODE
  (temporary one-time code)
        ↓
Step 4: App exchanges code for tokens
  app → Google: "here's the code + my client_secret"
  Google → app: "here's access_token + refresh_token"
        ↓
Step 5: App uses access_token to call Gmail API ✅
```

### Why the extra "code" step? Why not give token directly?

```
Security reason:

Authorization code:
  → sent through browser (visible, less secure)
  → useless without client_secret
  → one time use only

Token exchange:
  → happens server to server (secure)
  → requires client_secret (only app knows)
  → tokens never exposed in browser ✅
```

---

## Visual Flow

```
┌──────┐                                    ┌────────┐
│ You  │                                    │ Google │
└───┬──┘                                    └────┬───┘
    │                                            │
    │  1. click "Connect Gmail"                  │
    │ ──────────────────────────────────────────│
    │                                            │
    │  2. login + Allow                          │
    │ <──────────────────────────────────────── │
    │ ──────────────────────────────────────────│
    │                                            │
    │  3. redirect with CODE                     │
    │ <──────────────────────────────────────── │
    │                                            │
┌───┴──┐                                    ┌────┴───┐
│ App  │  4. exchange CODE + secret         │ Google │
│      │ ──────────────────────────────────>│        │
│      │  5. get access + refresh token     │        │
│      │ <──────────────────────────────────│        │
│      │                                    └────────┘
│      │  6. use access token               ┌────────┐
│      │ ──────────────────────────────────>│ Gmail  │
│      │  7. get emails                     │  API   │
│      │ <──────────────────────────────────│        │
└──────┘                                    └────────┘
```

---

# PART 5: OAUTH 1.0 vs OAUTH 2.0

| | OAuth 1.0 | OAuth 2.0 |
|--|-----------|-----------|
| Year | 2010 | 2012 |
| Complexity | Complex (cryptographic signatures) | Simpler |
| Signatures | Required for every request | Not required (uses HTTPS) |
| Tokens | Long-lived only | Access + Refresh tokens |
| Mobile support | Poor | Good |
| Used today | Rarely | Everywhere ✅ |

### Why OAuth 2.0 Won

```
OAuth 1.0 problems:
  → every request needed complex signature
  → hard to implement correctly
  → painful for mobile apps ❌

OAuth 2.0 improvements:
  → relies on HTTPS for security
  → simpler to implement
  → works great on mobile
  → separate short access token + long refresh token ✅
```

**Today: OAuth 2.0 is the standard. OAuth 1.0 is mostly dead.**

---

# PART 6: WHAT IS OPENID CONNECT?

## The Confusion

```
OAuth 2.0      = for AUTHORIZATION (what you can access)
OpenID Connect = for AUTHENTICATION (who you are)
```

## The Problem OpenID Solves

```
OAuth 2.0 only says:
  "this app can access photos"
  but does NOT tell the app WHO the user is ❌

OpenID Connect adds:
  "this app can access photos
   AND here's who the user is (name, email)" ✅
```

## OpenID = OAuth 2.0 + Identity Layer

```
OpenID Connect is built ON TOP of OAuth 2.0

OAuth 2.0:      gives access_token (for data access)
OpenID Connect: ALSO gives id_token (for identity)
```

## Real Example — "Login with Google"

```
When you see "Login with Google" button:
  → that's OpenID Connect ✅
  → app learns WHO you are (authentication)

When app accesses your Google Drive:
  → that's OAuth 2.0 ✅
  → app gets permission to access data (authorization)
```

## ID Token (JWT)

```
OpenID gives an id_token in JWT format:

{
  "sub": "1234567890",        ← unique user id
  "name": "Abishek",          ← your name
  "email": "abishek@gmail.com",
  "picture": "https://...",   ← profile pic
  "exp": 1234567890           ← expiry
}

App decodes this → knows who you are ✅
```

---

# PART 7: WHY DO WE NEED OAUTH?

## Reasons

```
1. SECURITY
   → never share your password with third party apps
   → apps get limited tokens, not your password ✅

2. LIMITED ACCESS (Scopes)
   → app only gets what it needs
   → photo app can't read your email ✅

3. REVOCABLE
   → take back access anytime
   → revoke token without changing password ✅

4. NO PASSWORD STORAGE
   → app never stores your password
   → if app is hacked → your password is safe ✅

5. TIME LIMITED
   → access tokens expire
   → stolen token only works briefly ✅
```

---

# PART 8: KEY TERMS QUICK REFERENCE

```
Resource Owner    → you (the user)
Client            → the app wanting access
Auth Server       → who gives permission (Google login)
Resource Server   → where data lives (Gmail API)

Authentication    → WHO you are
Authorization     → WHAT you can access

Scope             → specific permissions requested
Access Token      → short-lived key to access data
Refresh Token     → long-lived key to get new access tokens
ID Token          → contains your identity info (OpenID)
Authorization Code → temporary code exchanged for tokens

client_id         → public app identifier
client_secret     → private app password
redirect_uri      → where Google sends you back after login
```

---

# PART 9: HOW IT ALL CONNECTS (Gmail Example)

```
Our Gmail MCP setup mapped to OAuth terms:

credentials.json
  → contains client_id + client_secret
  → your app's identity

Auth command (npx ... auth)
  → started Authorization Code Flow
  → opened Google login (Authorization Server)

You logged in + clicked Allow
  → you (Resource Owner) granted permission
  → scopes: gmail.modify, gmail.settings.basic

Google gave authorization code
  → exchanged for tokens

token.json saved
  → access_token (1 hour)
  → refresh_token (long term)

When agent reads Gmail
  → MCP server uses access_token
  → calls Gmail API (Resource Server)
  → when expired → uses refresh_token for new one ✅
```

---

# SUMMARY — ONE LINE EACH

```
OAuth          = give limited access without sharing password
Authentication = who you are
Authorization  = what you can access
Scope          = specific permissions
Access Token   = short-lived data access key
Refresh Token  = gets new access tokens
OpenID Connect = OAuth + identity (who you are)
OAuth 2.0      = the modern standard (OAuth 1.0 is dead)
```