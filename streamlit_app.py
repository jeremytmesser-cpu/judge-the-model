"""Streamlit app for the judge-the-model exercise.

This app reads the exported results files and helps a clinical lead compare models,
choose a threshold, and assess whether a model is overfit.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

import m11

TRAIN = "Training"
TEST = "Test"
SECTIONS = ["1. Beyond Accuracy", "2. A Threshold for the Job", "3. Training vs. Test"]

st.set_page_config(page_title="Judge the Model", layout="wide")


@st.cache_data
def load(name: str):
    return m11.load(name)


def recommendations() -> None:
    d = load("decisions")
    recs = (d or {}).get("recommendations", {})
    with st.container(border=True):
        st.subheader("Recommendations")
        if not any(recs.values()):
            st.caption("No recommendations yet: fill in Recommendations in DECISIONS.md, run python -m analysis, and commit the updated results.")
            return
        for key in m11.DATASETS:
            st.markdown(f"**{m11.DATASET_LABEL[key]}:** {recs.get(key) or '_not written yet_'}")


# Section 1: beyond accuracy

def beyond_accuracy(res: dict, model: str) -> None:
    p, y = m11.preds(res, model)
    c = m11.confusion(p, y, 0.5)
    m = m11.metrics(c)
    st.caption(f"{TEST} · {m11.MODEL_LABEL[model]} at threshold 0.50")
    st.markdown(f"Positive class: **{m11.DATASET_LABEL[res['dataset']].lower()}**. A patient is flagged when the model probability is at least 0.50.")

    confusion_df = pd.DataFrame(
        [{
            "True positive": c["tp"],
            "False negative": c["fn"],
            "False positive": c["fp"],
            "True negative": c["tn"],
            "Accuracy": m11.fmt_pct(m["accuracy"]),
        }]
    )
    st.table(confusion_df)

    metrics_df = pd.DataFrame([
        {
            "Sensitivity / recall": m11.fmt_pct(m["sensitivity"]),
            "Specificity": m11.fmt_pct(m["specificity"]),
            "False positive rate": m11.fmt_pct(m["fpr"]),
            "Precision": m11.fmt_pct(m["precision"]),
            "F1": m11.fmt_pct(m["f1"]),
            "Flagged per 100": f"{m['flagged_per_100']:.1f}",
        }
    ])
    st.table(metrics_df)


# Section 2: threshold selection

def threshold(res: dict, model: str) -> None:
    p, y = m11.preds(res, model)
    threshold_value = st.slider("Threshold", min_value=0.10, max_value=0.90, value=0.50, step=0.01)
    c = m11.confusion(p, y, threshold_value)
    m = m11.metrics(c)

    st.caption(f"{TEST} · {m11.MODEL_LABEL[model]} at threshold {threshold_value:.2f}")
    st.table(pd.DataFrame([
        {
            "Threshold": f"{threshold_value:.2f}",
            "Sensitivity": m11.fmt_pct(m["sensitivity"]),
            "Specificity": m11.fmt_pct(m["specificity"]),
            "Precision": m11.fmt_pct(m["precision"]),
            "FPR": m11.fmt_pct(m["fpr"]),
            "Flagged per 100": f"{m['flagged_per_100']:.1f}",
        }
    ]))

    comp = pd.DataFrame([
        {
            "Metric": "Sensitivity / recall",
            "At 0.50": m11.fmt_pct(m11.metrics(m11.confusion(p, y, 0.5))["sensitivity"]),
            "At chosen threshold": m11.fmt_pct(m["sensitivity"]),
        },
        {
            "Metric": "Specificity",
            "At 0.50": m11.fmt_pct(m11.metrics(m11.confusion(p, y, 0.5))["specificity"]),
            "At chosen threshold": m11.fmt_pct(m["specificity"]),
        },
        {
            "Metric": "Precision",
            "At 0.50": m11.fmt_pct(m11.metrics(m11.confusion(p, y, 0.5))["precision"]),
            "At chosen threshold": m11.fmt_pct(m["precision"]),
        },
    ])
    st.caption("Compared with a 0.50 threshold")
    st.table(comp)


# Section 3: training vs test

def train_vs_test(res: dict, model: str) -> None:
    s = m11.auroc_summary(res)
    rows = [{
        "Model": m11.MODEL_LABEL[m],
        f"{TRAIN} AUROC": m11.fmt_num(v["train"]),
        f"{TEST} AUROC": m11.fmt_num(v["test"]),
        "Gap": m11.fmt_num(v["gap"]),
    } for m, v in s.items()]
    st.caption(f"{TRAIN} and {TEST} AUROC for every model")
    st.table(pd.DataFrame(rows).set_index("Model"))


RENDER = dict(zip(SECTIONS, [beyond_accuracy, threshold, train_vs_test]))

st.title("Judge the Model")
st.caption("Which classifier would you trust for this job, at what threshold, and with what limits?")
recommendations()
section = st.sidebar.radio("Section", SECTIONS)
key = st.sidebar.selectbox("Dataset", m11.DATASETS, format_func=m11.DATASET_LABEL.get)
res = load(key)
model = st.sidebar.selectbox("Model", m11.MODELS, format_func=lambda m: m11.MODEL_LABEL[m] + ("" if m in res["models"] else " (not trained yet)"))

st.header(section)
st.caption(f"{m11.DATASET_LABEL[key]}: {res['train']['n']:,} training rows ({res['train']['n_pos']:,} positive), {res['test']['n']:,} test rows ({res['test']['n_pos']:,} positive).")

if model in res["models"]:
    RENDER[section](res, model)
else:
    st.warning(f"{m11.MODEL_LABEL[model]} has no results yet: run python -m analysis, then commit and push results/.")
