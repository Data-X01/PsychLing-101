from pathlib import Path
import pandas as pd


DATASET_DIR = Path(__file__).resolve().parent
INPUT_PATH = DATASET_DIR / "original_data" / "time_data.csv"
OUTPUT_PATH = DATASET_DIR / "processed_data" / "exp1.csv"


def infer_correct_response(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for (cit1, cit2), g in df.groupby(["Cit1", "Cit2"], dropna=False):
        acc_by_resp = g.groupby("resp")["accuracy"].mean().to_dict()

        acc_a = acc_by_resp.get("a")
        acc_l = acc_by_resp.get("l")

        direct = None
        if pd.notna(acc_a) and pd.notna(acc_l):
            if acc_a > acc_l:
                direct = "a"
            elif acc_l > acc_a:
                direct = "l"

        rows.append(
            {
                "Cit1": cit1,
                "Cit2": cit2,
                "acc_a": acc_a,
                "acc_l": acc_l,
                "direct_inference": direct,
            }
        )

    pair_df = pd.DataFrame(rows)
    direct_lookup = {
        (r.Cit1, r.Cit2): r.direct_inference for r in pair_df.itertuples(index=False)
    }

    def resolve(row):
        if row["direct_inference"] is not None:
            return row["direct_inference"]

        reverse = direct_lookup.get((row["Cit2"], row["Cit1"]))
        if reverse == "a":
            return "l"
        if reverse == "l":
            return "a"

        manual_overrides = {
            ("Bologna", "Taranto"): "a",
            ("Taranto", "Bologna"): "l",
        }
        return manual_overrides.get((row["Cit1"], row["Cit2"]))

    pair_df["correct_response"] = pair_df.apply(resolve, axis=1)
    return pair_df[["Cit1", "Cit2", "correct_response"]]


def main():
    df = pd.read_csv(INPUT_PATH, sep=";", dtype=str)

    expected_cols = ["Cit2", "Cit1", "ID", "age", "gender", "hand", "resp", "RTs", "accuracy"]
    if list(df.columns) != expected_cols:
        raise ValueError(f"Unexpected columns: {list(df.columns)}")

    df = df.rename(
        columns={
            "Cit1": "city_left",
            "Cit2": "city_right",
            "ID": "participant_id",
            "RTs": "rt_raw",
            "resp": "response_raw",
        }
    ).copy()

    df["age"] = pd.to_numeric(df["age"], errors="raise").astype("Int64")
    df["accuracy"] = pd.to_numeric(df["accuracy"], errors="raise").astype("Int64")

    df["hand_raw"] = df["hand"]
    df["hand"] = df["hand"].str.strip().str.upper()

    df["rt_ms"] = pd.to_numeric(df["rt_raw"].str.replace(",", ".", regex=False), errors="raise")

    valid_resp = {"a", "l"}
    bad_resp = sorted(set(df["response_raw"]) - valid_resp)
    if bad_resp:
        raise ValueError(f"Unexpected response codes: {bad_resp}")

    pair_key = infer_correct_response(
        df.rename(columns={"city_left": "Cit1", "city_right": "Cit2", "response_raw": "resp"})
    )

    unresolved = pair_key[pair_key["correct_response"].isna()]
    if not unresolved.empty:
        raise ValueError(
            "Unresolved correct_response for ordered pairs:\n"
            + unresolved.to_string(index=False)
        )

    df = df.merge(
        pair_key,
        left_on=["city_left", "city_right"],
        right_on=["Cit1", "Cit2"],
        how="left",
        validate="many_to_one",
    ).drop(columns=["Cit1", "Cit2"])

    df["response_side"] = df["response_raw"].map({"a": "left", "l": "right"})
    df["correct_side"] = df["correct_response"].map({"a": "left", "l": "right"})
    df["response_correct"] = (df["response_raw"] == df["correct_response"]).astype("Int64")

    if not (df["response_correct"] == df["accuracy"]).all():
        mismatch = df.loc[df["response_correct"] != df["accuracy"]].head(20)
        raise ValueError(
            "Derived response_correct does not match accuracy.\n"
            + mismatch.to_string(index=False)
        )

    out_cols = [
        "participant_id",
        "age",
        "gender",
        "hand",
        "hand_raw",
        "city_left",
        "city_right",
        "response_raw",
        "response_side",
        "correct_response",
        "correct_side",
        "accuracy",
        "response_correct",
        "rt_raw",
        "rt_ms",
    ]

    df = df[out_cols].sort_values(
        ["participant_id", "city_left", "city_right"], kind="stable"
    ).reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Wrote: {OUTPUT_PATH}")
    print(f"Rows: {len(df)}")
    print(f"Participants: {df['participant_id'].nunique()}")
    print(f"Mean accuracy: {df['accuracy'].mean():.6f}")
    print(f"Mean RT ms: {df['rt_ms'].mean():.6f}")


if __name__ == "__main__":
    main()
