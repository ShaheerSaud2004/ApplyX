# 🔑 Admin Credentials Setup Guide

This guide shows you exactly what credentials you need to configure to run the Teemo AI platform in production.

## 📋 Required Credentials Checklist

### ✅ **Essential (Required for basic functionality)**
- [ ] OpenAI API Key
- [ ] Secret Key
- [ ] Admin User Password

**Note**: LinkedIn credentials are no longer needed in environment - users input them securely through the Profile page!

### 💳 **Stripe (Required for payments)**
- [ ] Stripe Secret Key
- [ ] Stripe Publishable Key
- [ ] Stripe Webhook Secret
- [ ] Stripe Price IDs

### 📧 **Email (Optional - for notifications)**
- [ ] SendGrid API Key
- [ ] From Email Address

### 🔒 **Security (Recommended)**
- [ ] Encryption Key
- [ ] Hash Salt

---

## 🛠️ **Step-by-Step Setup**

### 1. **Copy Environment File**
```bash
cp env.example .env
```

### 2. **Configure Essential Credentials**

#### **OpenAI API Key** 🤖
```bash
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
```

#### **LinkedIn Credentials** 🔗
**NEW: Each user enters their own LinkedIn credentials!**

LinkedIn credentials are now entered by **each individual user** through the Profile page in the web interface. This means:

- ✅ **Multi-user support**: Each user can use their own LinkedIn account
- ✅ **Secure storage**: Credentials are encrypted per user
- ✅ **No hardcoding**: No need to set LinkedIn credentials in environment files

> ⚠️ **Important**: Recommend users create a dedicated LinkedIn account for job applications.

#### **Application Security** 🔐
```bash
# Generate a strong secret key (32+ characters)
SECRET_KEY=your-super-secret-key-change-this-to-something-random-and-long

# Frontend URL for CORS
FRONTEND_URL=http://localhost:3000
```

### 3. **Configure Stripe for Payments** 💳

#### **Get Stripe Keys**
1. Sign up at [stripe.com](https://stripe.com)
2. Go to Developers → API keys
3. Copy your keys:

```bash
# Test keys (for development)
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key-here
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key-here
```

#### **Create Products and Prices**
1. Go to Stripe Dashboard → Products
2. Create products:
   - **Basic Plan**: $10/month
   - **Pro Plan**: $20/month
3. Copy the price IDs:

```bash
STRIPE_BASIC_PRICE_ID=price_your-basic-plan-price-id
STRIPE_PRO_PRICE_ID=price_your-pro-plan-price-id
```

#### **Setup Webhook**
1. Go to Stripe Dashboard → Webhooks
2. Add endpoint: `https://yourdomain.com/api/stripe/webhook`
3. Select events: `checkout.session.completed`, `invoice.payment_succeeded`, `customer.subscription.deleted`
4. Copy webhook secret:

```bash
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret-here
```

### 4. **Configure Email Notifications** 📧 (Optional)

#### **SendGrid Setup**
1. Sign up at [sendgrid.com](https://sendgrid.com)
2. Create API key with Mail Send permissions
3. Verify your sending domain

```bash
SENDGRID_API_KEY=SG.your-sendgrid-api-key-here
FROM_EMAIL=noreply@yourdomain.com
```

### 5. **Additional Security** 🔒 (Recommended)

```bash
# Generate random encryption key for sensitive data
ENCRYPTION_KEY=your-32-byte-encryption-key-here

# Salt for hashing sensitive data
HASH_SALT=your-random-hash-salt-here
```

---

## 🏃‍♂️ **Quick Start Commands**

### 1. **Setup Database & Dependencies**
```bash
python3 migrate_db.py
```

### 2. **Start Backend**
```bash
cd backend && python3 app.py
```

### 3. **Start Frontend** (New Terminal)
```bash
npm run dev
```

### 4. **Run Tests** (New Terminal)
```bash
python3 test_e2e.py
```

---

## 👑 **Admin Access**

### **Default Admin Account**
- **Email**: `admin@teemoai.com`
- **Password**: `admin123`
- **Dashboard**: `http://localhost:3000/admin`

> ⚠️ **SECURITY**: Change the admin password immediately after first login!

---

## 🔧 **Production Configuration**

### **Environment Variables for Production**

```bash
# Production URLs
FRONTEND_URL=https://yourdomain.com
BACKEND_URL=https://api.yourdomain.com

# Production Stripe keys (live mode)
STRIPE_SECRET_KEY=sk_live_your-live-stripe-secret-key
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_your-live-stripe-publishable-key

# Strong encryption in production
ENCRYPTION_KEY=generate-strong-32-byte-key-for-production
HASH_SALT=generate-unique-salt-for-production

# Production database (if using PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database
```

### **Security Checklist for Production**
- [ ] Use HTTPS for all endpoints
- [ ] Set strong SECRET_KEY (32+ random characters)
- [ ] Use live Stripe keys, not test keys
- [ ] Configure proper CORS origins
- [ ] Set up database backups
- [ ] Enable rate limiting
- [ ] Use a dedicated LinkedIn account
- [ ] Set up monitoring and logging

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Backend won't start**
```bash
# Check if all required packages are installed
pip install -r backend/requirements.txt

# Check database connection
python3 migrate_db.py
```

#### **Stripe payments fail**
- Verify your Stripe keys are correct
- Check webhook endpoint is accessible
- Ensure price IDs match your Stripe products

#### **LinkedIn bot fails**
- Verify LinkedIn credentials are correct
- Check if LinkedIn account requires 2FA (disable it)
- Make sure ChromeDriver is installed and accessible

#### **Frontend won't load**
```bash
# Install dependencies
npm install

# Check for build errors
npm run build

# Start in development mode
npm run dev
```

### **Log Files**
- Backend logs: Check terminal where `python3 app.py` is running
- Frontend logs: Check browser developer console
- Bot logs: Check terminal output and `bot_logs.txt`

---

## 📊 **Testing Your Setup**

### **Quick Health Check**
```bash
# Test backend health
curl http://localhost:5000/api/health

# Test frontend
curl http://localhost:3000
```

### **Full End-to-End Test**
```bash
python3 test_e2e.py
```

### **Manual Testing Steps**
1. ✅ Register a new account at `http://localhost:3000`
2. ✅ Login with your credentials
3. ✅ Upload a resume PDF
4. ✅ Check dashboard shows quota (5/5 for free users)
5. ✅ Try to start the agent (should work if quota available)
6. ✅ Test Stripe checkout (if configured)
7. ✅ Access admin dashboard with admin credentials

---

## 🎯 **Production Deployment Checklist**

Before going live, ensure:

- [ ] All credentials are set in production `.env`
- [ ] Database is set up and migrated
- [ ] Stripe is configured with live keys
- [ ] Webhook endpoints are accessible
- [ ] SSL certificates are configured
- [ ] Domain DNS is pointing to your server
- [ ] Admin password has been changed
- [ ] Backup systems are in place
- [ ] Monitoring is configured

---

## 🆘 **Support**

If you encounter issues:

1. **Check the logs** in your terminal where the services are running
2. **Run the test suite** to identify specific problems
3. **Verify all credentials** are correctly set in `.env`
4. **Check network connectivity** for external services (OpenAI, Stripe, etc.)

---

## 🔒 **Security Best Practices**

1. **Never commit** `.env` files to version control
2. **Use strong passwords** for all accounts
3. **Enable 2FA** where possible (except LinkedIn bot account)
4. **Regularly rotate** API keys and secrets
5. **Monitor** for suspicious activity
6. **Backup** your database regularly
7. **Keep dependencies** updated

---

**🎉 Ready to launch your AI-powered job application SaaS!** 