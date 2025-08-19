# 🚀 Vercel Deployment Guide

## Next.js Frontend Deployment

This project includes a Next.js frontend that can be deployed to Vercel for production use.

### Prerequisites

- Node.js 18+ installed locally
- Vercel account
- Access to your database (Neon, PostgreSQL, etc.)

### Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

### Environment Variables

For database connectivity, use the following environment variable naming conventions:

#### Database Connection Variables

- `DB_DATABASE_URL` — pooled connection string (recommended for production workloads)
- `DB_DATABASE_URL_UNPOOLED` — direct connection string (for special cases requiring direct connections)
- `DB_PGHOST` — PostgreSQL host
- `DB_PGUSER` — PostgreSQL username  
- `DB_PGDATABASE` — PostgreSQL database name
- `DB_PGPASSWORD` — PostgreSQL password

#### Recommended Configuration

- **Development**: Use `DB_DATABASE_URL` for consistent pooled connections
- **Production**: Keep `DB_DATABASE_URL` (pooled) for optimal performance
- **Testing**: Use `DB_DATABASE_URL_UNPOOLED` if you need direct database access

### Vercel Deployment Configuration

The project includes:

- `vercel.json` - Vercel deployment configuration
- `next.config.js` - Next.js build settings
- `postcss.config.js` - PostCSS configuration for Tailwind
- `tailwind.config.js` - Tailwind CSS configuration

### Environment Setup in Vercel

1. Go to your Vercel project settings
2. Navigate to **Environment Variables**
3. Add the following variables:

```bash
DB_DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
DB_DATABASE_URL_UNPOOLED=postgresql://user:password@host:port/database?sslmode=require
# Add other DB_ variables as needed
```

### Neon Database Integration

When using Neon as your database provider:

#### Environment Variable Configuration
- Enable Neon DB for Development, Preview, and Production environments
- For preview deployments, keep "create database branch" enabled
- For Production, you can disable database branch creation if not needed

#### Connection String Format
Ensure your connection strings include `?sslmode=require` for Neon compatibility:
```
DB_DATABASE_URL=postgresql://user:password@host.neon.tech:5432/database?sslmode=require
```

### Python Backend Integration Example

If you need to connect from Python server code or serverless functions:

```python
import os
import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/query")
def query_db():
    conn_str = os.environ.get("DB_DATABASE_URL", "")
    if not conn_str:
        return jsonify({"error": "Database URL not set"}), 500

    try:
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        result = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"postgres_version": result[0]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
```

### Troubleshooting

#### Common Issues
- **Database connection failed**: Confirm `DB_` environment variables are set in Vercel settings
- **SSL connection required**: Ensure `?sslmode=require` is present in your database URL
- **Preview deployment issues**: Check Neon resource quotas and database branch creation settings

#### Debug Steps
1. Test database connection locally with `.env.local` file
2. Verify the exact environment variables injected by Vercel match your local setup
3. Monitor Vercel deployment logs for connection errors
4. Check Neon dashboard for connection activity and errors

#### Security Notes
- Rotate database credentials regularly (every 90 days recommended)
- Never commit database URLs or credentials to version control
- Use Vercel's secure environment variable storage
- Monitor for exposed credentials in logs and rotate immediately if found

### Build and Deployment

```bash
# Build for production
npm run build

# Deploy to Vercel (automatic on git push)
# Or manually: vercel --prod
```

The application will be available at your Vercel domain with full database connectivity and optimized performance.