export default function Dashboard() {
  return (
    <main className="min-h-screen p-8">
      <header className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-semibold mb-2">Triune Oracle — Monitoring Dashboard</h1>
        <p className="text-sm text-slate-600">Minimal Next.js scaffold to resolve Vercel deployment and host the Oracle dashboard.</p>
      </header>

      <section className="max-w-4xl mx-auto mt-8 grid gap-6 md:grid-cols-2">
        <div className="p-6 bg-white rounded-lg shadow">
          <h2 className="text-lg font-medium">System Status</h2>
          <p className="mt-2 text-slate-500">No live integrations configured yet. This panel will surface workflow run summaries and alerts.</p>
        </div>

        <div className="p-6 bg-white rounded-lg shadow">
          <h2 className="text-lg font-medium">Recent Activity</h2>
          <p className="mt-2 text-slate-500">Placeholders for recent workflow runs, PR merges, and artifacts.</p>
        </div>
      </section>
    </main>
  );
}