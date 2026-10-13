import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
from scipy.stats import pearsonr, spearmanr

# -----------------------
# Style constants (requested)
# -----------------------
COLOR_N = "#BBBDC0"
COLOR_PEARSON = "#F8BB15"
COLOR_SPEARMAN = "#39499B"

DASH_SOLID = [1, 0]
DASH_DOTTED = [3, 3]  # dotted-looking

COEFF_DECIMALS = 4
PVAL_DECIMALS = 5

# -----------------------
# Page config
# -----------------------
st.set_page_config(page_title="Cumulative δ13C–δ18O Correlation Tests", layout="wide")
st.title("Cumulative δ13C–δ18O Correlation Tests")

st.caption(
    "Input: stratigraphic level from the base (m), δ13C, δ18O. "
    "Run either downward (from the top) or upward (from the base) cumulative tests. "
    "Coefficients are shown with 4 decimals; p-values with 5 decimals."
)

# -----------------------
# Input table
# -----------------------
st.subheader("Input table (paste from Excel)")
df0 = pd.DataFrame(
    {
        "level_m_from_base": [0.0, 1.0, 2.0],
        "d13C": [np.nan, np.nan, np.nan],
        "d18O": [np.nan, np.nan, np.nan],
    }
)

df = st.data_editor(df0, num_rows="dynamic", use_container_width=True)

# -----------------------
# Options
# -----------------------
c1, c2 = st.columns(2)
min_n = c1.number_input("Minimum n to start computing", min_value=3, max_value=500, value=3, step=1)
missing_mode = c2.selectbox("Missing-data handling", ["Pairwise delete (recommended)", "Stop at first missing"], index=0)

st.divider()

# -----------------------
# Core stats helpers
# -----------------------
def _safe_pearson(x: np.ndarray, y: np.ndarray):
    if len(x) < 3 or np.nanstd(x) == 0 or np.nanstd(y) == 0:
        return np.nan, np.nan
    r, p = pearsonr(x, y)
    return float(r), float(p)

def _safe_spearman(x: np.ndarray, y: np.ndarray):
    if len(x) < 3 or np.nanstd(x) == 0 or np.nanstd(y) == 0:
        return np.nan, np.nan
    rho, p = spearmanr(x, y)  # ranks recomputed within each subset; ties handled
    return float(rho), float(p)

def _prep_input(inp: pd.DataFrame) -> pd.DataFrame:
    work = inp.copy()

    # Coerce numeric
    for col in ["level_m_from_base", "d13C", "d18O"]:
        work[col] = pd.to_numeric(work[col], errors="coerce")

    # Drop fully empty rows
    work = work.dropna(how="all", subset=["level_m_from_base", "d13C", "d18O"]).reset_index(drop=True)

    return work

# -----------------------
# Downward cumulative (from the top)
# -----------------------
def compute_downward(work: pd.DataFrame) -> pd.DataFrame:
    """
    Order: uppermost -> downward (i.e., highest level first)
    x: cumulative m from the top = top_level - current_level (>=0)
    Table rows expand from uppermost downward.
    """
    w = work.copy()
    if len(w) == 0:
        return w

    # Uppermost = maximum level
    w = w.sort_values("level_m_from_base", ascending=False, kind="mergesort").reset_index(drop=True)

    top_level = float(w.loc[0, "level_m_from_base"])
    w["cumulative_m_from_top"] = top_level - w["level_m_from_base"]

    out = pd.DataFrame(
        {
            "cumulative_m_from_top": w["cumulative_m_from_top"],
            "n": np.nan,
            "pearson_r": np.nan,
            "pearson_p": np.nan,
            "spearman_rho": np.nan,
            "spearman_p": np.nan,
        }
    )

    for i in range(len(w)):
        subset = w.loc[:i, ["d13C", "d18O"]].copy()

        if missing_mode.startswith("Stop") and subset.isna().any().any():
            break

        used = subset.dropna() if missing_mode.startswith("Pairwise") else subset
        n = len(used)
        out.at[i, "n"] = n

        if n < min_n:
            continue

        x = used["d13C"].to_numpy(dtype=float)
        y = used["d18O"].to_numpy(dtype=float)

        pr, pp = _safe_pearson(x, y)
        sr, sp = _safe_spearman(x, y)

        out.at[i, "pearson_r"] = pr
        out.at[i, "pearson_p"] = pp
        out.at[i, "spearman_rho"] = sr
        out.at[i, "spearman_p"] = sp

    # Formatting for display
    out["cumulative_m_from_top"] = out["cumulative_m_from_top"].round(4)
    out["pearson_r"] = out["pearson_r"].round(COEFF_DECIMALS)
    out["spearman_rho"] = out["spearman_rho"].round(COEFF_DECIMALS)
    out["pearson_p"] = out["pearson_p"].round(PVAL_DECIMALS)
    out["spearman_p"] = out["spearman_p"].round(PVAL_DECIMALS)

    return out

# -----------------------
# Upward cumulative (from the base)
# -----------------------
def compute_upward(work: pd.DataFrame) -> pd.DataFrame:
    """
    Order: lowermost -> upward (i.e., lowest level first)
    x: cumulative m from the base = current_level - base_level (>=0)
    Table rows expand from lowermost upward.
    Chart x-axis should show 0 at right and increase to the left (reverse x).
    """
    w = work.copy()
    if len(w) == 0:
        return w

    # Lowermost = minimum level
    w = w.sort_values("level_m_from_base", ascending=True, kind="mergesort").reset_index(drop=True)

    base_level = float(w.loc[0, "level_m_from_base"])
    w["cumulative_m_from_base"] = w["level_m_from_base"] - base_level

    out = pd.DataFrame(
        {
            "cumulative_m_from_base": w["cumulative_m_from_base"],
            "n": np.nan,
            "pearson_r": np.nan,
            "pearson_p": np.nan,
            "spearman_rho": np.nan,
            "spearman_p": np.nan,
        }
    )

    for i in range(len(w)):
        subset = w.loc[:i, ["d13C", "d18O"]].copy()

        if missing_mode.startswith("Stop") and subset.isna().any().any():
            break

        used = subset.dropna() if missing_mode.startswith("Pairwise") else subset
        n = len(used)
        out.at[i, "n"] = n

        if n < min_n:
            continue

        x = used["d13C"].to_numpy(dtype=float)
        y = used["d18O"].to_numpy(dtype=float)

        pr, pp = _safe_pearson(x, y)
        sr, sp = _safe_spearman(x, y)

        out.at[i, "pearson_r"] = pr
        out.at[i, "pearson_p"] = pp
        out.at[i, "spearman_rho"] = sr
        out.at[i, "spearman_p"] = sp

    # Formatting for display
    out["cumulative_m_from_base"] = out["cumulative_m_from_base"].round(4)
    out["pearson_r"] = out["pearson_r"].round(COEFF_DECIMALS)
    out["spearman_rho"] = out["spearman_rho"].round(COEFF_DECIMALS)
    out["pearson_p"] = out["pearson_p"].round(PVAL_DECIMALS)
    out["spearman_p"] = out["spearman_p"].round(PVAL_DECIMALS)

    return out

# -----------------------
# Chart builder (single chart with dual y-axes)
# -----------------------
def build_chart(
    out: pd.DataFrame,
    x_col: str,
    x_title: str,
    reverse_x: bool,
    title: str
):
    """
    Left y-axis: -1..1 for coefficients AND p-values (as requested)
    Right y-axis: n (natural numbers)
    """
    plot = out.copy()

    # Long format for 4 lines (pearson r / pearson p / spearman rho / spearman p)
    left_long = pd.DataFrame(
        {
            "x": pd.concat([plot[x_col]] * 4, ignore_index=True),
            "value": pd.concat(
                [plot["pearson_r"], plot["pearson_p"], plot["spearman_rho"], plot["spearman_p"]],
                ignore_index=True
            ),
            "series": (
                ["Pearson coefficient"] * len(plot)
                + ["Pearson p-value"] * len(plot)
                + ["Spearman coefficient"] * len(plot)
                + ["Spearman p-value"] * len(plot)
            ),
        }
    )

    # Color + dash maps (as requested)
    color_scale = alt.Scale(
        domain=["Pearson coefficient", "Pearson p-value", "Spearman coefficient", "Spearman p-value"],
        range=[COLOR_PEARSON, COLOR_PEARSON, COLOR_SPEARMAN, COLOR_SPEARMAN],
    )
    dash_scale = alt.Scale(
        domain=["Pearson coefficient", "Pearson p-value", "Spearman coefficient", "Spearman p-value"],
        range=[DASH_SOLID, DASH_DOTTED, DASH_SOLID, DASH_DOTTED],
    )

    x_enc = alt.X(
        "x:Q",
        title=x_title,
        scale=alt.Scale(reverse=reverse_x)
    )

    left_lines = alt.Chart(left_long).mark_line().encode(
        x=x_enc,
        y=alt.Y("value:Q", title="Coefficients and p-values", scale=alt.Scale(domain=[-1, 1])),
        color=alt.Color("series:N", scale=color_scale, legend=alt.Legend(title="Series")),
        strokeDash=alt.StrokeDash("series:N", scale=dash_scale),
        tooltip=[alt.Tooltip("x:Q", title="x"), alt.Tooltip("series:N"), alt.Tooltip("value:Q", format=".6f")],
    )

    n_line = alt.Chart(plot).mark_line(color=COLOR_N).encode(
        x=alt.X(f"{x_col}:Q", title=x_title, scale=alt.Scale(reverse=reverse_x)),
        y=alt.Y("n:Q", title="n (pairs)", axis=alt.Axis(orient="right")),
        tooltip=[alt.Tooltip(x_col + ":Q"), alt.Tooltip("n:Q")],
    )

    chart = alt.layer(left_lines, n_line).resolve_scale(y="independent").properties(
        title=title,
        height=720
    )
    return chart

# -----------------------
# Buttons
# -----------------------
b1, b2 = st.columns(2)
down_btn = b1.button("Downward cumulative", type="primary")
up_btn = b2.button("Upward cumulative", type="primary")

work = _prep_input(df)

if down_btn:
    if len(work) == 0:
        st.error("No valid rows found. Please paste numeric values into the input table.")
        st.stop()

    out = compute_downward(work)

    st.subheader("Downward cumulative results (from the top)")
    st.dataframe(
        out.rename(columns={
            "cumulative_m_from_top": "cumulative_m_from_top",
            "n": "n",
            "pearson_r": "pearson_coefficient",
            "pearson_p": "pearson_p_value",
            "spearman_rho": "spearman_coefficient",
            "spearman_p": "spearman_p_value",
        }),
        use_container_width=True
    )

    chart = build_chart(
        out=out,
        x_col="cumulative_m_from_top",
        x_title="Cumulative m from the top",
        reverse_x=False,  # 0 at left, increases to right
        title="Downward cumulative: coefficients & p-values vs. cumulative m from the top (n on right axis)"
    )
    st.altair_chart(chart, use_container_width=True)

if up_btn:
    if len(work) == 0:
        st.error("No valid rows found. Please paste numeric values into the input table.")
        st.stop()

    out = compute_upward(work)

    st.subheader("Upward cumulative results (from the base)")
    st.dataframe(
        out.rename(columns={
            "cumulative_m_from_base": "cumulative_m_from_base",
            "n": "n",
            "pearson_r": "pearson_coefficient",
            "pearson_p": "pearson_p_value",
            "spearman_rho": "spearman_coefficient",
            "spearman_p": "spearman_p_value",
        }),
        use_container_width=True
    )

    chart = build_chart(
        out=out,
        x_col="cumulative_m_from_base",
        x_title="Cumulative m from the base",
        reverse_x=True,  # 0 at right, increases to left
        title="Upward cumulative: coefficients & p-values vs. cumulative m from the base (n on right axis)"
    )
    st.altair_chart(chart, use_container_width=True)
