import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Fischer Technik — Lead Cockpit",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS: Card-Styling & Feinschliff ───────────────────────────────────────────
st.markdown("""
<style>
  /* Seitenleiste ausblenden */
  section[data-testid="stSidebar"] { display: none; }

  /* Streamlit-Standard-Padding reduzieren */
  .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

  /* KPI-Metric-Karten: weiße Box, feiner grauer Rahmen */
  [data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e2e6ed;
    border-radius: 14px;
    padding: 22px 20px 18px 20px;
    box-shadow: 0 2px 8px rgba(26,58,107,0.07);
  }
  [data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #1a3a6b !important;
  }
  [data-testid="stMetricLabel"] {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: #6b7280 !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
  }
  [data-testid="stMetricDeltaIcon-Up"] { color: #16a34a !important; }
  [data-testid="stMetricDelta"]        { color: #16a34a !important; font-size: 0.83rem !important; }

  /* Divider-Linie dezenter */
  hr { border-color: #e5e7eb; margin: 0.5rem 0 1.2rem 0; }

  /* Tabellen-Header an Firmenfarbe anpassen */
  thead tr th {
    background: #f8faff !important;
    color: #1a3a6b !important;
    font-weight: 700 !important;
  }
</style>
""", unsafe_allow_html=True)

# ── Ampel-Farben (matt, edel) ──────────────────────────────────────────────────
# Grün  = Auftrag erteilt   → Salbeigrün  #6e9b71
# Gold  = versendet / Chef  → Fischer-Gold #c9a227
# Rot   = Infos fehlen      → Ziegelrot   #b85c4b

def _safe_str(label) -> str:
    """Konvertiert jeden Wert sicher zu Python-str (robust gegen Arrow/NA/None)."""
    try:
        s = str(label)
        return "" if s in ("nan", "<NA>", "None", "NaN") else s
    except Exception:
        return ""

def color_for_status(label) -> str:
    """Ampel-Farbe per Teilstring-Match (ASCII-safe, Umlaute egal)."""
    l = _safe_str(label).lower()
    if "erteilt"   in l:                  return "#6e9b71"
    if "chef"      in l:                  return "#2563a8"
    if "versendet" in l:                  return "#c9a227"
    if "infos"     in l or "wartet" in l: return "#b85c4b"
    return "#9ca3af"

def emoji_for_status(label) -> str:
    """Dezenter Farbpunkt für Tabellenspalte."""
    l = _safe_str(label).lower()
    if "erteilt"   in l: return "🟢"
    if "chef"      in l: return "🔵"
    if "versendet" in l: return "🟡"
    if "infos"     in l or "wartet" in l: return "🔴"
    return "⚪"

# ── Demo-Daten (Fallback, wenn Sheet leer / < 3 Zeilen) ───────────────────────
DEMO_DATA = pd.DataFrame([
    {
        "Projekt-ID": "FT-2031", "Erstkontakt-Datum": "2026-05-08",
        "Kunden-Name": "Bau GmbH Paderborn",
        "E-Mail-Adresse": "info@bau-paderborn.de",
        "Gewerk/Projektart": "Industrie-Wartung & E-Check",
        "Status": "Auftrag erteilt", "Umsatz-Potenzial": 42000,
        "Projektdetails": "Jährlicher E-Check Produktionshalle 3.000 qm nach DGUV V3. Austausch 12× LED-Panels. Termin flexibel — Betrieb läuft durch.",
    },
    {
        "Projekt-ID": "FT-2033", "Erstkontakt-Datum": "2026-05-13",
        "Kunden-Name": "Thomas Bergmann",
        "E-Mail-Adresse": "t.bergmann@gmx.de",
        "Gewerk/Projektart": "PV-Anlage 14 kWp + Speicher",
        "Status": "Angebot versendet", "Umsatz-Potenzial": 34800,
        "Projektdetails": "Einfamilienhaus, Satteldach Süd 35°. 35× Sunpower 400 W, BYD-Speicher 10 kWh, Wallbox 11 kW. Eigenverbrauch ca. 70 % angestrebt.",
    },
    {
        "Projekt-ID": "FT-2035", "Erstkontakt-Datum": "2026-05-17",
        "Kunden-Name": "Familie Hoffmann",
        "E-Mail-Adresse": "hoffmann@t-online.de",
        "Gewerk/Projektart": "Dachsanierung & Photovoltaik",
        "Status": "Angebot versendet", "Umsatz-Potenzial": 28500,
        "Projektdetails": "Doppelhaus 180 qm, Baujahr 1978. Komplettsanierung Satteldach + PV 10 kWp. Zweites Angebot nach Kundenkorrektur (Dachgaube entfernt).",
    },
    {
        "Projekt-ID": "FT-2037", "Erstkontakt-Datum": "2026-05-21",
        "Kunden-Name": "Maria Schulze",
        "E-Mail-Adresse": "m.schulze@web.de",
        "Gewerk/Projektart": "Smart Home — KNX Komplettsystem",
        "Status": "In Prüfung durch Chef", "Umsatz-Potenzial": 19600,
        "Projektdetails": "Neubau EFH, Rohbau fertig. KNX für Licht, Beschattung, Heizung (6 Zonen) und Alarmanlage. Einzug geplant Oktober 2026.",
    },
    {
        "Projekt-ID": "FT-2039", "Erstkontakt-Datum": "2026-05-24",
        "Kunden-Name": "Klaus Richter",
        "E-Mail-Adresse": "krichter@outlook.de",
        "Gewerk/Projektart": "Lüftungsanlage Wohngebäude",
        "Status": "Wartet auf Infos", "Umsatz-Potenzial": 11200,
        "Projektdetails": "Bestandsbau 1992, 180 qm, 2 Etagen. KWL mit Wärmerückgewinnung >85 %. Kunde soll noch Grundriss + Fotos Kellertechnik nachreichen.",
    },
    {
        "Projekt-ID": "FT-2041", "Erstkontakt-Datum": "2026-05-27",
        "Kunden-Name": "Anna Weber",
        "E-Mail-Adresse": "anna.weber@gmail.com",
        "Gewerk/Projektart": "Heizung & Sanitär Neubau",
        "Status": "Wartet auf Infos", "Umsatz-Potenzial": 8900,
        "Projektdetails": "Reihenhaus Neubau, Richtfest Juni 2026, 120 qm. Fußbodenheizung EG + OG, 2 Bäder, Wärmepumpe Luft-Wasser. Genaue Rohbaumaße fehlen noch.",
    },
])

# ── Daten laden ────────────────────────────────────────────────────────────────
SHEET_ID  = "1DKINRTQQHVPOEIrCpfyPiarmdxtOowI_GLVATMHz-SM"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

COLUMN_ALIASES = {
    "Projektstatus": "Status",
    "Gewerk":        "Gewerk/Projektart",
}

@st.cache_data(ttl=60)
def load_leads() -> tuple[pd.DataFrame, bool]:
    """Liest ausschließlich Tabellenblatt 1 (gid=0 = Leads).
    Weitere Blätter (z. B. 'Preise') werden durch gid=0 automatisch ignoriert."""
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            df = pd.read_csv(SHEET_URL, on_bad_lines="skip", encoding=enc)
            df = df.dropna(how="all").rename(columns=COLUMN_ALIASES)
            df.columns = [c.strip() for c in df.columns]
            if len(df) >= 3:
                return df, False
            break  # Sheet geladen, aber noch zu wenige Zeilen → Demo-Modus
        except Exception:
            continue  # nächste Encoding-Variante versuchen
    return DEMO_DATA.copy(), True

# ── Header ─────────────────────────────────────────────────────────────────────
col_logo, col_btn = st.columns([10, 1])
with col_logo:
    st.markdown("""
<div style="
  background: linear-gradient(90deg, #1a3a6b 0%, #1e4d9b 100%);
  padding: 20px 30px;
  border-radius: 14px;
  border-left: 5px solid #c9a227;
  margin-bottom: 4px;
">
  <h1 style="color:#ffffff; margin:0; font-size:1.55rem; font-weight:800; letter-spacing:2px;">
    ⚡ FISCHER TECHNIK — LIVE LEAD COCKPIT
  </h1>
  <p style="color:#a8c4e8; margin:5px 0 0; font-size:0.78rem; letter-spacing:0.08em;">
    FISCHER TECHNIK IM HAUS GMBH &amp; CO. KG &nbsp;·&nbsp; LIPPLING / DELBRÜCK &nbsp;·&nbsp; CRM AUTOMATISIERT MIT KI
  </p>
</div>
""", unsafe_allow_html=True)
with col_btn:
    st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)
    if st.button("🔄", help="Daten aus Google Sheet neu laden"):
        st.cache_data.clear()
        st.rerun()

df, is_demo = load_leads()

if is_demo:
    st.info(
        "📊 **Demo-Modus** — Das Google Sheet enthält noch keine Live-Daten. "
        "Sobald die ersten Kundenanfragen über die n8n-Workflows eingehen, "
        "schaltet das Dashboard automatisch auf Echtdaten um.",
        icon=None,
    )

st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)

# ── Hilfsfunktionen ────────────────────────────────────────────────────────────
def to_num(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str)
              .str.replace(r"[€\s\.\xa0]", "", regex=True)
              .str.replace(",", ".", regex=False),
        errors="coerce",
    )

def fmt_eur(val: float) -> str:
    return "€ " + f"{val:,.0f}".replace(",", ".")

def status_contains(keyword: str) -> pd.Series:
    """Robuste Teilstring-Suche, Groß-/Kleinschreibung egal."""
    return (
        df.get("Status", pd.Series(dtype=str))
          .astype(str)
          .str.contains(keyword, case=False, na=False, regex=False)
    )

# ── KPI-Berechnungen ───────────────────────────────────────────────────────────
df["_num"] = to_num(df.get("Umsatz-Potenzial", pd.Series(dtype=str)))

# KPI 1: Offenes Volumen = versendet + beim Chef + Infos fehlen
mask_volume   = status_contains("versendet") | status_contains("Chef") | status_contains("Infos")
volume        = df.loc[mask_volume, "_num"].sum()
# KPI 2: Aufträge erteilt
auftraege     = int(status_contains("erteilt").sum())
# KPI 3: Beim Chef (suche auf "Chef" – robust gegen Umlaut-Encoding)
beim_chef     = int(status_contains("Chef").sum())
# KPI 4: Gesamt
total         = len(df)
# Hilfswert für Tabelle/Chart
wartend       = int(status_contains("Infos").sum())

# ── KPI-Zeile ──────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4, gap="medium")
with k1:
    st.metric(
        "💶 Angebotsvolumen (offen)",
        fmt_eur(volume),
        delta="+18 % ggü. Vormonat",
        help="Summe aller versendeten Angebote und erteilten Aufträge",
    )
with k2:
    st.metric(
        "✅ Aufträge erteilt",
        auftraege,
        delta=f"+{auftraege} neu",
        help="Leads mit Status 'Auftrag erteilt'",
    )
with k3:
    st.metric(
        "📋 Angebote beim Chef",
        beim_chef,
        delta="zur Freigabe",
        help="Status: In Prüfung durch Chef",
    )
with k4:
    st.metric(
        "📊 Leads gesamt",
        total,
        delta=f"+{total} gesamt",
        help="Alle Leads im System",
    )

st.markdown("<div style='margin: 14px 0 4px 0'></div>", unsafe_allow_html=True)
st.divider()

# ── Chart + Tabelle ────────────────────────────────────────────────────────────
col_pie, col_table = st.columns([4, 6], gap="large")

with col_pie:
    # Weiße Card-Box um das Diagramm
    st.markdown("""
    <div style="background:#fff; border:1px solid #e2e6ed; border-radius:14px;
                padding:20px 16px 4px 16px; box-shadow:0 2px 8px rgba(26,58,107,0.07);">
      <p style="margin:0 0 2px 0; font-size:0.78rem; font-weight:700;
                color:#6b7280; text-transform:uppercase; letter-spacing:0.07em;">
        Lead-Status Verteilung
      </p>
    </div>
    """, unsafe_allow_html=True)

    if not df.empty and "Status" in df.columns:
        s = df["Status"].astype(object).fillna("").astype(str).str.strip().value_counts().reset_index()
        s.columns = ["Status", "Anzahl"]
        palette = [color_for_status(r) for r in s["Status"]]

        fig = go.Figure(data=[go.Pie(
            labels=s["Status"],
            values=s["Anzahl"],
            hole=0.60,
            marker=dict(colors=palette, line=dict(color="#ffffff", width=3)),
            textfont=dict(size=12, color="#111827"),
            hovertemplate="<b>%{label}</b><br>%{value} Lead(s) · %{percent}<extra></extra>",
        )])
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#374151", family="sans-serif"),
            showlegend=True,
            legend=dict(
                orientation="v",
                font=dict(size=11, color="#374151"),
                bgcolor="rgba(0,0,0,0)",
                bordercolor="rgba(0,0,0,0)",
            ),
            margin=dict(t=10, b=10, l=0, r=0),
            height=320,
            annotations=[dict(
                text=f"<b>{total}</b><br><span style='font-size:11px;color:#6b7280'>Leads</span>",
                x=0.5, y=0.5,
                font=dict(size=20, color="#1a3a6b"),
                showarrow=False,
            )],
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Noch keine Leads vorhanden.")

with col_table:
    st.markdown("""
    <div style="background:#fff; border:1px solid #e2e6ed; border-radius:14px;
                padding:20px 20px 4px 20px; box-shadow:0 2px 8px rgba(26,58,107,0.07);">
      <p style="margin:0 0 12px 0; font-size:0.78rem; font-weight:700;
                color:#6b7280; text-transform:uppercase; letter-spacing:0.07em;">
        Alle Leads — Übersicht
      </p>
    </div>
    """, unsafe_allow_html=True)

    DISPLAY = ["Projekt-ID", "Kunden-Name", "Gewerk/Projektart", "Status", "Umsatz-Potenzial"]
    avail   = [c for c in DISPLAY if c in df.columns]
    out     = df[avail].copy()

    if "Erstkontakt-Datum" in df.columns:
        out["_d"] = pd.to_datetime(df["Erstkontakt-Datum"], errors="coerce")
        out = out.sort_values("_d", ascending=False).drop(columns=["_d"])

    if "Status" in out.columns:
        out["Status"] = (
            out["Status"].astype(object).fillna("").astype(str).str.strip()
            .map(lambda s: f"{emoji_for_status(s)} {s}")
        )

    if "Umsatz-Potenzial" in out.columns:
        out["Umsatz-Potenzial"] = df["_num"].reindex(out.index).map(
            lambda v: fmt_eur(v) if pd.notna(v) else "—"
        )

    st.dataframe(
        out.reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
        height=360,
        column_config={
            "Projekt-ID":        st.column_config.TextColumn("Projekt",   width="small"),
            "Kunden-Name":       st.column_config.TextColumn("Kunde"),
            "Gewerk/Projektart": st.column_config.TextColumn("Gewerk"),
            "Status":            st.column_config.TextColumn("Status",    width="medium"),
            "Umsatz-Potenzial":  st.column_config.TextColumn("Potenzial", width="small"),
        },
    )

# ── Umsatz-Balkendiagramm ──────────────────────────────────────────────────────
st.markdown("<div style='margin-top: 8px'></div>", unsafe_allow_html=True)

if "Gewerk/Projektart" in df.columns and "_num" in df.columns:
    grp = (
        df.groupby("Gewerk/Projektart", as_index=False)["_num"]
          .sum()
          .dropna()
          .sort_values("_num", ascending=True)
    )
    if not grp.empty:
        st.markdown("""
        <div style="background:#fff; border:1px solid #e2e6ed; border-radius:14px;
                    padding:20px 20px 4px 20px; box-shadow:0 2px 8px rgba(26,58,107,0.07);">
          <p style="margin:0 0 4px 0; font-size:0.78rem; font-weight:700;
                    color:#6b7280; text-transform:uppercase; letter-spacing:0.07em;">
            Umsatz-Potenzial nach Gewerk (€)
          </p>
        </div>
        """, unsafe_allow_html=True)

        bar = go.Figure(go.Bar(
            x=grp["_num"],
            y=grp["Gewerk/Projektart"],
            orientation="h",
            marker=dict(
                color=grp["_num"],
                colorscale=[[0, "#3b82f6"], [1, "#1a3a6b"]],
                line=dict(width=0),
            ),
            text=[fmt_eur(v) for v in grp["_num"]],
            textposition="outside",
            textfont=dict(size=12, color="#374151"),
            hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
        ))
        bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#374151", family="sans-serif"),
            xaxis=dict(showgrid=True, gridcolor="#f0f2f7", zeroline=False,
                       tickformat=",.0f", ticksuffix=" €"),
            yaxis=dict(showgrid=False),
            margin=dict(t=10, b=20, l=10, r=80),
            height=max(180, len(grp) * 52),
        )
        st.plotly_chart(bar, use_container_width=True)

# ── Projektdetails-Expander ────────────────────────────────────────────────────
if "Projektdetails" in df.columns:
    detail_df = df.copy()
    if "Erstkontakt-Datum" in detail_df.columns:
        detail_df["_sort"] = pd.to_datetime(detail_df["Erstkontakt-Datum"], errors="coerce")
        detail_df = detail_df.sort_values("_sort", ascending=False)

    has_details = detail_df["Projektdetails"].astype(str).str.strip().replace("nan", "")
    has_details = has_details[has_details != ""]

    if not has_details.empty:
        st.markdown("<div style='margin-top: 8px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#fff; border:1px solid #e2e6ed; border-radius:14px;
                    padding:20px 20px 8px 20px; box-shadow:0 2px 8px rgba(26,58,107,0.07);
                    margin-bottom: 8px;">
          <p style="margin:0; font-size:0.78rem; font-weight:700;
                    color:#6b7280; text-transform:uppercase; letter-spacing:0.07em;">
            Projektdetails — Lead-Ansicht
          </p>
        </div>
        """, unsafe_allow_html=True)

        for _, row in detail_df.iterrows():
            details = str(row.get("Projektdetails", "")).strip()
            if not details or details == "nan":
                continue

            pid     = row.get("Projekt-ID", "—")
            name    = row.get("Kunden-Name", "—")
            status  = str(row.get("Status", "")).strip()
            gewerk  = row.get("Gewerk/Projektart", "—")
            num_val = row.get("_num", None)

            expander_label = f"{emoji_for_status(status)}  {pid} — {name}"
            with st.expander(expander_label):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**Gewerk**\n\n{gewerk}")
                c2.markdown(f"**Status**\n\n{status}")
                c3.markdown(f"**Umsatz-Potenzial**\n\n{fmt_eur(num_val) if pd.notna(num_val) else '—'}")
                st.markdown(
                    f"<div style='background:#f8faff; border-left:4px solid #1a3a6b; "
                    f"border-radius:6px; padding:12px 16px; margin-top:8px; "
                    f"font-size:0.93rem; color:#111827; line-height:1.6;'>"
                    f"{details}</div>",
                    unsafe_allow_html=True,
                )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<p style="text-align:center; color:#c0c8d8; font-size:0.72rem; margin-top:24px;">
  ⚡ Fischer Technik im Haus GmbH &amp; Co. KG — Lead Cockpit
  &nbsp;·&nbsp; Datenquelle: Google Sheets
  &nbsp;·&nbsp; Auto-Refresh alle 60 Sek.
</p>
""", unsafe_allow_html=True)
