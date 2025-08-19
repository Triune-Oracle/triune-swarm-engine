import '../styles/globals.css'
import Head from 'next/head'

export default function App({ Component, pageProps }) {
  return (
    <>
      <Head>
        <title>Triune Oracle Monitoring Dashboard</title>
        <meta name="description" content="Real-time monitoring dashboard for the Triune Oracle Swarm Engine" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <Component {...pageProps} />
    </>
  )
}