## Voice Assistant Console Frontend

This app provides the management console for configuring AI voice assistants. It's built with
Next.js 14 (App Router), TypeScript, Tailwind CSS v4, and shadcn/ui components.

## Getting Started

Install dependencies and run the dev server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## UI Toolkit

- Tailwind CSS v4 with CSS variables for theming.
- shadcn/ui configured for the `src/` directory. Add more components with:

  ```bash
  npx shadcn@latest add <component-name>
  ```

## Environment

Copy `.env.example` to `.env.local` and configure the API endpoints exposed by FastAPI.

```bash
cp .env.example .env.local
```

Adjust `NEXT_PUBLIC_API_BASE_URL` to match your backend host.

## Available Scripts

- `npm run dev` – start the dev server on `http://localhost:3000`.
- `npm run build` – create an optimized production build.
- `npm run lint` – run Next.js lint checks.

You can deploy to any platform that supports Next.js 14 (Vercel, Netlify, Docker, etc.).
