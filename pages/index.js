import Head from 'next/head'
import OracleMonitoringDashboard from '../components/OracleMonitoringDashboard'

export default function Home() {
  return (
    <>
      <Head>
        <title>Triune Oracle Monitoring Dashboard</title>
        <meta name="description" content="Real-time monitoring dashboard for the Triune Oracle Swarm Engine" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main>
        <OracleMonitoringDashboard />
      </main>
    </>
  )
}