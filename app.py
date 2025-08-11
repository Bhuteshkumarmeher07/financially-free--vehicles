import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Vahan Investor Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("data/vahan_master_full.csv")
    df["date"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp()
    df["vehicle_category"] = df["vehicle_category"].astype(str).str.upper()
    df["manufacturer"] = df["manufacturer"].astype(str).str.strip()
    df["registrations"] = pd.to_numeric(df["registrations"], errors="coerce").fillna(0).astype(int)
    df["quarter"] = df["date"].dt.to_period("Q")
    df["year"] = df["date"].dt.year
    return df.sort_values(["date","vehicle_category","manufacturer"])

def yoy_qoq(df, group_cols):
    g = df.groupby(["quarter"] + group_cols, as_index=False)["registrations"].sum().sort_values("quarter")
    if group_cols:  # per-category / per-manufacturer
        g["prev_q"] = g.groupby(group_cols)["registrations"].shift(1)
        g["prev_y"] = g.groupby(group_cols)["registrations"].shift(4)
    else:          # total market (no grouping keys)
        g["prev_q"] = g["registrations"].shift(1)
        g["prev_y"] = g["registrations"].shift(4)
    g["qoq_pct"] = np.where(g["prev_q"] > 0, (g["registrations"] - g["prev_q"]) / g["prev_q"] * 100, np.nan)
    g["yoy_pct"] = np.where(g["prev_y"] > 0, (g["registrations"] - g["prev_y"]) / g["prev_y"] * 100, np.nan)
    return g


def enough_for_qoq(dfq):  # need ≥ 2 quarters for at least one series
    return dfq["quarter"].nunique() >= 2

def enough_for_yoy(dfq):  # need ≥ 5 quarters for at least one series (to have t and t-4)
    return dfq["quarter"].nunique() >= 5

def latest_quarter(df):
    return df["quarter"].max()

def insights_block(df):
    # High-level total-market view
    q = yoy_qoq(df, [])
    if q.empty:
        return ["Not enough data to compute insights."]
    LQ = latest_quarter(q)
    row = q[q["quarter"]==LQ].tail(1)  # aggregated market
    qoq = float(row["qoq_pct"].iloc[0]) if row["qoq_pct"].notna().any() else None
    yoy = float(row["yoy_pct"].iloc[0]) if row["yoy_pct"].notna().any() else None

    # Per-category deltas
    cq = yoy_qoq(df, ["vehicle_category"])
    latest_cat = cq[cq["quarter"]==LQ].copy()

    notes = []
    if qoq is not None:
        notes.append(f"Total market QoQ: **{qoq:+.1f}%** in {LQ}.")
    else:
        notes.append(f"Total market QoQ: **n/a** (need ≥2 quarters).")
    if yoy is not None:
        notes.append(f"Total market YoY: **{yoy:+.1f}%** in {LQ}.")
    else:
        notes.append(f"Total market YoY: **n/a** (need ≥5 quarters).")

    if not latest_cat.empty:
        # Best / worst category by QoQ and YoY
        if latest_cat["qoq_pct"].notna().any():
            best_qoq = latest_cat.sort_values("qoq_pct", ascending=False).iloc[0]
            worst_qoq = latest_cat.sort_values("qoq_pct", ascending=True).iloc[0]
            notes.append(f"Best QoQ category: **{best_qoq['vehicle_category']} {best_qoq['qoq_pct']:+.1f}%**; "
                         f"Weakest QoQ: **{worst_qoq['vehicle_category']} {worst_qoq['qoq_pct']:+.1f}%**.")
        if latest_cat["yoy_pct"].notna().any():
            best_yoy = latest_cat.sort_values("yoy_pct", ascending=False).iloc[0]
            notes.append(f"Strongest YoY category: **{best_yoy['vehicle_category']} {best_yoy['yoy_pct']:+.1f}%**.")

    # Top manufacturers (by latest quarter size) and their momentum
    mq = yoy_qoq(df, ["vehicle_category","manufacturer"])
    latest_m = mq[mq["quarter"]==LQ].copy()
    if not latest_m.empty:
        # size = current registrations
        top = latest_m.sort_values("registrations", ascending=False).groupby("vehicle_category").head(5)
        # Pick 1–2 callouts per category
        for cat in sorted(top["vehicle_category"].unique()):
            tcat = top[top["vehicle_category"]==cat]
            # pick the best QoQ mover among top size
            tcat_q = tcat.dropna(subset=["qoq_pct"])
            if not tcat_q.empty:
                best = tcat_q.sort_values("qoq_pct", ascending=False).iloc[0]
                notes.append(f"In **{cat}**, **{best['manufacturer']}** shows QoQ **{best['qoq_pct']:+.1f}%** with "
                             f"{int(best['registrations']):,} registrations in {LQ}.")
    return notes

# ----------------- UI -----------------
df = load_data()
st.title("Vehicle Registrations — Investor View (YoY & QoQ)")
st.caption("Source: Vahan Dashboard | Categories: 2W, 3W, 4W | Manufacturer-wise, monthly")

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    min_date, max_date = df["date"].min(), df["date"].max()
    sdate = st.date_input("Start date", value=min_date.date(), min_value=min_date.date(), max_value=max_date.date())
    edate = st.date_input("End date", value=max_date.date(), min_value=min_date.date(), max_value=max_date.date())
    cats = sorted(df["vehicle_category"].unique().tolist())
    mans = sorted(df["manufacturer"].unique().tolist())
    sel_cats = st.multiselect("Vehicle Categories", cats, default=cats)
    sel_mans = st.multiselect("Manufacturers (optional)", mans, default=[])

# Apply filters
mask = (df["date"]>=pd.to_datetime(sdate)) & (df["date"]<=pd.to_datetime(edate)) & (df["vehicle_category"].isin(sel_cats))
if sel_mans:
    mask &= df["manufacturer"].isin(sel_mans)
dff = df[mask].copy()

# KPIs
st.subheader("Key Metrics")
k1,k2,k3,k4 = st.columns(4)
latest_month = dff["date"].max()
latest_total = dff[dff["date"]==latest_month]["registrations"].sum()
k1.metric("Latest Month Total", f"{int(latest_total):,}")

agg_total = yoy_qoq(dff, [])
if not agg_total.empty:
    LQ = latest_quarter(agg_total)
    last = agg_total[agg_total["quarter"]==LQ].tail(1)
    qoq = last["qoq_pct"].iloc[0] if last["qoq_pct"].notna().any() else None
    yoy = last["yoy_pct"].iloc[0] if last["yoy_pct"].notna().any() else None
    k2.metric("QoQ % (Total)", f"{qoq:.1f}%" if pd.notna(qoq) else "—")
    k3.metric("YoY % (Total)", f"{yoy:.1f}%" if pd.notna(yoy) else "—")
    k4.metric("Latest Quarter", str(LQ))
else:
    k2.metric("QoQ % (Total)","—"); k3.metric("YoY % (Total)","—"); k4.metric("Latest Quarter","—")

st.divider()

# Category trends
st.subheader("Category Trends")
cat_m = dff.groupby(["date","vehicle_category"], as_index=False)["registrations"].sum()
if not cat_m.empty:
    st.plotly_chart(px.line(cat_m, x="date", y="registrations", color="vehicle_category", markers=True,
                            title="Monthly Registrations by Category"), use_container_width=True)
else:
    st.info("No data after filters.")

# Category growth bars (QoQ / YoY)
cat_q = yoy_qoq(dff, ["vehicle_category"])
if not cat_q.empty:
    LQ = latest_quarter(cat_q)
    latest_cat = cat_q[cat_q["quarter"]==LQ]
    c1,c2 = st.columns(2)
    if enough_for_qoq(cat_q):
        c1.plotly_chart(px.bar(latest_cat, x="vehicle_category", y="qoq_pct",
                               title=f"QoQ % by Category ({LQ})"), use_container_width=True)
    else:
        c1.info("QoQ needs ≥ 2 quarters.")
    if enough_for_yoy(cat_q):
        c2.plotly_chart(px.bar(latest_cat, x="vehicle_category", y="yoy_pct",
                               title=f"YoY % by Category ({LQ})"), use_container_width=True)
    else:
        c2.info("YoY needs ≥ 5 quarters (to compare with same quarter last year).")

st.divider()

# Manufacturer view
st.subheader("Top Manufacturers (Latest Quarter)")
man_q = yoy_qoq(dff, ["vehicle_category","manufacturer"])
if not man_q.empty:
    LQ = latest_quarter(man_q)
    latest_m = man_q[man_q["quarter"]==LQ].copy()
    # take top N by registrations within each category
    topn = st.slider("Top N per category", 5, 25, 10)
    top_m = latest_m.sort_values("registrations", ascending=False).groupby("vehicle_category").head(topn)
    m1, m2 = st.columns(2)
    m1.plotly_chart(px.bar(top_m, x="manufacturer", y="registrations", color="vehicle_category",
                           title=f"Top Manufacturers — Total Registrations ({LQ})"), use_container_width=True)
    if enough_for_qoq(man_q):
        m2.plotly_chart(px.bar(top_m, x="manufacturer", y="qoq_pct", color="vehicle_category",
                               title=f"Top Manufacturers — QoQ % ({LQ})"), use_container_width=True)
    else:
        m2.info("QoQ needs ≥ 2 quarters.")
else:
    st.info("Not enough data for manufacturer view with current filters.")

st.divider()

# Auto-generated investor insights
st.subheader("Investor Insights (Auto)")
for line in insights_block(dff):
    st.markdown(f"- {line}")

st.caption("Tip: Positive **YoY** = structural growth; Positive **QoQ** = near-term momentum. Track consistency across both.")
