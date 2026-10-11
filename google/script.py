import os
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

def generate_stock_chart_html(ticker_symbol: str = "GOOG", days_history: int = 10, output_filename: str = "index.html"):
    """
    Stiahne dáta z yfinance, ošetrí MultiIndex štruktúru stĺpcov,
    vytvorí Plotly graf a exportuje ho do HTML pre GitHub Pages.
    """
    # 2. Získanie dát
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days_history + 10)

    df = yf.download(
        ticker_symbol,
        start=start_date.strftime('%Y-%m-%d'),
        end=end_date.strftime('%Y-%m-%d'),
        auto_adjust=True,
        progress=False
    )

    if df.empty:
        raise ValueError(f"Nepodarilo sa stiahnuť žiadne dáta pre ticker {ticker_symbol}.")

    # 🔥 OPRAVA KEYERROR: Odstránenie MultiIndexu zo stĺpcov, ak existuje
    if isinstance(df.columns, go.Layout or any): # Poistka pre rôzne typy indexov
        pass

    # Ak sú stĺpce vo formáte (Metric, Ticker), vezmeme len Metric (napr. 'Close')
    if df.columns.nlevels > 1:
        df.columns = df.columns.get_level_values(0)

    # Pre istotu ošetríme situáciu, kedy by stĺpce zostali ako objekty
    df.columns = [str(col) for col in df.columns]

    # Výber posledných 10 obchodných dní
    df = df.tail(days_history)

    # Bezpečné vytiahnutie hodnôt
    y_values = df['Close'].values.flatten()
    x_values = df.index

    # 3. Vytvorenie grafu pomocou Plotly Object Oriented API
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x_values,
        y=y_values,
        mode='lines+markers',
        name='Zatváracia cena',
        line=dict(color='#1A73E8', width=3),
        marker=dict(size=8, color='#1A73E8', symbol='circle'),
        hovertemplate='<b>Dátum:</b> %{x|%d.%m.%Y}<br><b>Cena:</b> $%{y:.2f}<extra></extra>'
    ))

    # 4. Profesionálny vizuálny tuning
    fig.update_layout(
        title=dict(
            text=f"Vývoj uzatváracej ceny akcie {ticker_symbol} (Posledných {days_history} obchodných dní)",
            font=dict(size=20, color='#1F2937', family="Arial, sans-serif"),
            x=0.05
        ),
        xaxis=dict(
            title="Dátum",
            gridcolor='#E5E7EB',
            linecolor='#9CA3AF',
            tickformat='%d.%m.',
            tickmode='linear'
        ),
        yaxis=dict(
            title="Cena v USD ($)",
            gridcolor='#E5E7EB',
            linecolor='#9CA3AF',
            tickprefix="$",
            tickformat=".2f"
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=60, r=40, t=80, b=60),
        hovermode='x unified',
        autosize=True
    )

    # 5. Generovanie čistého HTML kódu pre web
    plotly_div = fig.to_html(
        include_plotlyjs='cdn',
        full_html=False,
        config={'displayModeBar': False, 'responsive': True}
    )

    html_content = f"""<!DOCTYPE html>
<html lang="sk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Akcie {ticker_symbol} - Prehľad</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #F9FAFB;
            color: #111827;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }}
        .container {{
            width: 90%;
            max-width: 1000px;
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            margin: 20px 0;
        }}
        header {{
            text-align: center;
            margin-bottom: 20px;
        }}
        h1 {{
            margin: 0;
            color: #111827;
            font-size: 2rem;
        }}
        p {{
            color: #6B7280;
            margin: 5px 0 0 0;
        }}
        footer {{
            margin-top: 20px;
            font-size: 0.85rem;
            color: #9CA3AF;
        }}
    </style>
</head>
<body>

    <div class="container">
        <header>
            <h1>Finančný Dashboard</h1>
            <p>Automaticky generovaný report pre ticker {ticker_symbol}</p>
        </header>

        <!-- Tu sa prilepí interaktívny Plotly graf -->
        {plotly_div}
    </div>

    <footer>
        Dáta poskytnuté cez Yahoo Finance API. Aktualizované: {datetime.now().strftime('%d.%m.%Y %H:%M')}
    </footer>

</body>
</html>
"""

    # Uloženie súboru do prostredia Colab
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✔️ HTML stránka bola úspešne vytvorená a uložená ako '{output_filename}'")

# Spustenie funkcie
generate_stock_chart_html(ticker_symbol="GOOG", days_history=10, output_filename="index.html")
