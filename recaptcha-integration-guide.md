
# 🛡️ Google reCAPTCHA Integration Guide

## What's Available

### 1. reCAPTCHA v2
Classic “I’m not a robot” checkbox or invisible version.

Add this to your HTML form:

```html
<script src="https://www.google.com/recaptcha/api.js" async defer></script>
<div class="g-recaptcha" data-sitekey="YOUR_SITE_KEY"></div>
```

---

### 2. reCAPTCHA v3

Completely invisible; returns a score (0–1) for risk analysis.

Example:

```html
<script src="https://www.google.com/recaptcha/api.js?render=YOUR_SITE_KEY"></script>
<script>
  grecaptcha.ready(function() {
    grecaptcha.execute('YOUR_SITE_KEY', {action: 'submit'}).then(function(token) {
      // Add token to form submission
    });
  });
</script>
```

---

### 3. reCAPTCHA Enterprise

For high-security or enterprise-scale needs (fraud detection, WAFs, mobile SDKs).

Requires [Google Cloud Console setup](https://cloud.google.com/recaptcha-enterprise/docs/set-up)

---

## 🔧 Integration Steps

### 1. Register and Get Keys

Visit: [reCAPTCHA Admin Console](https://www.google.com/recaptcha/admin/create)

Choose version (v2/v3/Enterprise), register your domain/app, and get:

- Site Key (for frontend)
- Secret Key (for server-side validation)

---

### 2. Client-side Setup

**For v2:**

```html
<script src="https://www.google.com/recaptcha/api.js" async defer></script>
<div class="g-recaptcha" data-sitekey="YOUR_SITE_KEY"></div>
```

**For v3:**

```html
<script src="https://www.google.com/recaptcha/api.js?render=YOUR_SITE_KEY"></script>
<script>
  grecaptcha.ready(function() {
    grecaptcha.execute('YOUR_SITE_KEY', {action: 'submit'}).then(function(token) {
      // Send token with form
    });
  });
</script>
```

---

### 3. Server-side Verification

Send a POST request to:

```
https://www.google.com/recaptcha/api/siteverify
```

With these parameters:

- `secret`: your secret key
- `response`: the token from the client
- `remoteip`: (optional) user's IP

#### Example in Node.js (Express):

```js
const axios = require('axios');
const secretKey = 'YOUR_SECRET_KEY';

app.post('/verify', async (req, res) => {
  const token = req.body.token;
  const verification = await axios.post(
    'https://www.google.com/recaptcha/api/siteverify',
    null,
    {
      params: {
        secret: secretKey,
        response: token,
      },
    }
  );

  const success = verification.data.success;
  if (success) {
    // Proceed with action
  } else {
    // Block or show error
  }
});
```

---

## 🚀 Enterprise Use?

- Use [Google Cloud Console](https://console.cloud.google.com/)
- Enable reCAPTCHA Enterprise API
- Follow: [reCAPTCHA Enterprise Quickstart](https://cloud.google.com/recaptcha-enterprise/docs/quickstart)

---

## 🔗 Resources

- [reCAPTCHA Docs (v2 & v3)](https://developers.google.com/recaptcha/)
- [reCAPTCHA Admin Console](https://www.google.com/recaptcha/admin/create)
- [reCAPTCHA Enterprise](https://cloud.google.com/recaptcha-enterprise)

---

## ✅ Summary Checklist

- ✅ Choose reCAPTCHA version
- ✅ Register site and obtain keys
- ✅ Embed client-side code
- ✅ Verify token on the backend
- ✅ Monitor scores, responses, and bot traffic in the admin console
