from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .metric import score_events
from .postprocess import load_config, predictions_to_submission


PRED_COLS = ["p_onset", "p_wakeup", "p_sleep", "p_invalid"]


def blend_prediction_files(paths: list[str], weights: list[float]) -> pd.DataFrame:
    if len(paths) != len(weights):
        raise ValueError("--weights length must match --pred length")
    if not paths:
        raise ValueError("at least one prediction file is required")

    rows = []
    for path, weight in zip(paths, weights):
        if weight < 0:
            raise ValueError("weights must be non-negative")
        df = pd.read_parquet(path)
        missing = [c for c in ["series_id", "step", *PRED_COLS] if c not in df.columns]
        if missing:
            raise ValueError(f"{path} missing columns: {missing}")
        tmp = df[["series_id", "step", *PRED_COLS]].copy()
        tmp["_weight"] = float(weight)
        for col in PRED_COLS:
            tmp[col] = tmp[col].astype("float64") * tmp["_weight"]
        rows.append(tmp)

    all_pred = pd.concat(rows, ignore_index=True)
    agg = all_pred.groupby(["series_id", "step"], sort=False, as_index=False)[[*PRED_COLS, "_weight"]].sum()
    weight = agg["_weight"].to_numpy(dtype="float64")
    if np.any(weight <= 0):
        raise ValueError("all blended rows must have positive total weight")
    for col in PRED_COLS:
        agg[col] = (agg[col].to_numpy(dtype="float64") / weight).astype("float32")
    return agg.drop(columns="_weight")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pred", nargs="+", required=True)
    parser.add_argument("--weights", nargs="+", type=float, required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--config")
    parser.add_argument("--events", default="/kaggle/input/competitions/child-mind-institute-detect-sleep-states/train_events.csv")
    parser.add_argument("--submission-out")
    args = parser.parse_args()

    pred = blend_prediction_files(args.pred, args.weights)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pred.to_parquet(out_path, index=False)
    print(f"wrote blended predictions: {out_path}")

    if args.config:
        cfg = load_config(args.config)
        sub = predictions_to_submission(pred, cfg)
        if args.submission_out:
            sub_path = Path(args.submission_out)
            sub_path.parent.mkdir(parents=True, exist_ok=True)
            sub.to_csv(sub_path, index=False)
            print(f"wrote submission: {sub_path}")
        if Path(args.events).exists():
            events = pd.read_csv(args.events).dropna(subset=["step"])
            events_val = events[events["series_id"].isin(pred["series_id"].unique())]
            score = score_events(events_val, sub, cfg["postprocess"]["tolerances_steps"])
            print(f"OOF local score: {score}")
            print(sub.shape)
            print(sub["event"].value_counts())
            print(sub["score"].describe())


if __name__ == "__main__":
    main()
