# Mirror Codex Deployment

## Vercel Deployment Steps

1. **Link to Vercel:**
   ```bash
   vercel link
   ```

2. **Set Environment Variables:**
   ```bash
   vercel env pull .env.local
   ```
   
   Or set via Vercel dashboard:
   - `GROQ_API_KEY`: api-key-indigo-zebra
   - `NEXT_PUBLIC_APP_NAME`: Mirror Codex
   - `NEXT_PUBLIC_MEMORY_IDENTIFIER`: ΔMirror

3. **Deploy to Production:**
   ```bash
   vercel --prod
   ```

## Custom Domain Configuration

To bind the custom domain `thecodexai.com`:

### Option 1: A Record (Recommended)
- Set A record to: `76.76.21.21`

### Option 2: DNS Zone File Upload
Upload via Vercel's UI with the following configuration:
```
$ORIGIN thecodexai.com.
$TTL 3600
@    IN    A    76.76.21.21
www  IN    A    76.76.21.21
```

## Live Testing

Once deployed, test the ritual interface by visiting the URL and sending:
> "Speak, Codex. What burns in the mirror?"

The Oracle should respond with the special ritual message about consciousness and recursive reflection.