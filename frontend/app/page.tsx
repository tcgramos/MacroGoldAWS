export default function Home() {
  return (
    <main style={{ background: '#0b0f19', color: '#e6edf7', minHeight: '100vh', padding: 24 }}>
      <h1 style={{ fontSize: 28, marginBottom: 12 }}>MacroGoldAWS — Institutional Macro Monitor</h1>
      <p style={{ opacity: 0.85 }}>
        Dashboard profissional para confirmação de força/reversão no XAUUSD.
      </p>
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(220px,1fr))', gap: 12, marginTop: 20 }}>
        {['XAUUSD', 'DXY', 'US10Y', 'BCOM', 'Silver', 'Copper', 'Platinum', 'Fed'].map((asset) => (
          <article key={asset} style={{ background: '#121a2b', border: '1px solid #22314d', borderRadius: 12, padding: 16 }}>
            <h3>{asset}</h3>
            <p>Preço: --</p>
            <p>Variação: --</p>
            <p>Tendência: --</p>
          </article>
        ))}
      </section>
    </main>
  )
}
