# Next.js Oracle Monitoring Dashboard

This directory contains the Next.js configuration files needed for Vercel deployment of the Triune Oracle Monitoring Dashboard.

## Files Added for Vercel Deployment

### Configuration Files
- `package.json` - Node.js dependencies and scripts
- `vercel.json` - Vercel deployment configuration  
- `next.config.js` - Next.js configuration
- `tailwind.config.js` - Tailwind CSS configuration
- `postcss.config.js` - PostCSS configuration

### Application Files
- `pages/index.js` - Main dashboard page
- `pages/_app.js` - Next.js app configuration
- `components/OracleMonitoringDashboard.jsx` - Main dashboard component
- `styles/globals.css` - Global CSS with Tailwind

## Development Commands

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Dashboard Features

The Oracle Monitoring Dashboard provides:
- Real-time performance monitoring of Oracle, Conjuror, Gemini, Aria, and Capri components
- Live task tracking and status updates
- System logs with real-time updates
- Interactive command console
- Responsive design with Tailwind CSS

## Deployment

The dashboard is configured to deploy automatically on Vercel when changes are pushed to the repository. The `vercel.json` file contains all necessary deployment configuration.

## Note

This Next.js setup is designed to coexist with the existing Python codebase without interference. The Python components remain fully functional while providing a modern web interface for monitoring.