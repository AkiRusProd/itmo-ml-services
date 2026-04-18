#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.error import URLError

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


RANDOM_STATE = 42


@dataclass
class ModelResult:
    name: str
    mae: float
    rmse: float
    r2: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Train a regression model for real-estate price prediction, "
            "validate it on a hold-out split, and save the best pipeline."
        )
    )
    parser.add_argument(
        "--dataset",
        choices=["california_housing", "csv"],
        default="california_housing",
        help="Dataset source. Use california_housing by default, or csv for a custom file.",
    )
    parser.add_argument(
        "--data-path",
        type=Path,
        help="Path to a CSV file. Required when --dataset=csv.",
    )
    parser.add_argument(
        "--target-column",
        default="target",
        help="Target column name for CSV datasets.",
    )
    parser.add_argument(
        "--artifacts-dir",
        type=Path,
        default=Path("artifacts"),
        help="Directory for the trained model and metadata.",
    )
    parser.add_argument(
        "--model-path",
        type=Path,
        default=None,
        help="Full path to save the model. Defaults to <artifacts-dir>/apartment_price_model.joblib.",
    )
    parser.add_argument(
        "--metrics-path",
        type=Path,
        default=None,
        help="Full path to save training metadata. Defaults to <artifacts-dir>/training_metrics.json.",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Validation split size.",
    )
    return parser.parse_args()


def load_dataset(
    args: argparse.Namespace, dataset_cache_dir: Path
) -> tuple[pd.DataFrame, pd.Series, dict[str, Any]]:
    if args.dataset == "california_housing":
        try:
            dataset = fetch_california_housing(
                as_frame=True,
                data_home=str(dataset_cache_dir),
            )
        except URLError as exc:
            raise RuntimeError(
                "Failed to download California Housing dataset. "
                "If you are offline, rerun later with network access or pass "
                "--dataset csv --data-path <path-to-csv> --target-column <column>."
            ) from exc
        features = dataset.frame.drop(columns=[dataset.target.name]).copy()
        target = dataset.frame[dataset.target.name].copy()
        metadata = {
            "source": "sklearn.fetch_california_housing",
            "target_name": dataset.target.name,
            "feature_names": list(features.columns),
            "dataset_note": (
                "California Housing is a good bootstrap dataset for regression, "
                "but it describes districts rather than specific apartments. "
                "For production realism you can later switch to a CSV with apartment-level features."
            ),
        }
        return features, target, metadata

    if args.data_path is None:
        raise ValueError("--data-path is required when --dataset=csv")

    frame = pd.read_csv(args.data_path)
    if args.target_column not in frame.columns:
        raise ValueError(
            f"Target column '{args.target_column}' not found in {args.data_path}"
        )

    features = frame.drop(columns=[args.target_column]).copy()
    target = frame[args.target_column].copy()
    metadata = {
        "source": str(args.data_path),
        "target_name": args.target_column,
        "feature_names": list(features.columns),
        "dataset_note": "Custom CSV dataset loaded from disk.",
    }
    return features, target, metadata


def build_preprocessor(features: pd.DataFrame) -> ColumnTransformer:
    numeric_features = features.select_dtypes(include=["number"]).columns.tolist()
    categorical_features = [column for column in features.columns if column not in numeric_features]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_features),
            ("cat", categorical_pipeline, categorical_features),
        ],
        remainder="drop",
    )


def build_candidate_models() -> dict[str, Any]:
    return {
        "gradient_boosting": GradientBoostingRegressor(random_state=RANDOM_STATE),
        "random_forest": RandomForestRegressor(
            n_estimators=250,
            max_depth=None,
            min_samples_leaf=2,
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
    }


def evaluate_model(
    model_name: str,
    estimator: Any,
    preprocessor: ColumnTransformer,
    x_train: pd.DataFrame,
    x_val: pd.DataFrame,
    y_train: pd.Series,
    y_val: pd.Series,
) -> tuple[Pipeline, ModelResult]:
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", estimator),
        ]
    )

    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_val)

    result = ModelResult(
        name=model_name,
        mae=float(mean_absolute_error(y_val, predictions)),
        rmse=float(np.sqrt(mean_squared_error(y_val, predictions))),
        r2=float(r2_score(y_val, predictions)),
    )
    return pipeline, result


def main() -> None:
    args = parse_args()
    artifacts_dir = args.artifacts_dir
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    model_path = args.model_path or artifacts_dir / "apartment_price_model.joblib"
    metrics_path = args.metrics_path or artifacts_dir / "training_metrics.json"

    dataset_cache_dir = artifacts_dir / ".sklearn_data"
    dataset_cache_dir.mkdir(parents=True, exist_ok=True)

    features, target, dataset_metadata = load_dataset(args, dataset_cache_dir)
    x_train, x_val, y_train, y_val = train_test_split(
        features,
        target,
        test_size=args.test_size,
        random_state=RANDOM_STATE,
    )

    candidates = build_candidate_models()
    model_results: list[ModelResult] = []
    best_pipeline: Pipeline | None = None
    best_result: ModelResult | None = None

    for model_name, estimator in candidates.items():
        preprocessor = build_preprocessor(features)
        pipeline, result = evaluate_model(
            model_name=model_name,
            estimator=estimator,
            preprocessor=preprocessor,
            x_train=x_train,
            x_val=x_val,
            y_train=y_train,
            y_val=y_val,
        )
        model_results.append(result)
        if best_result is None or result.rmse < best_result.rmse:
            best_pipeline = pipeline
            best_result = result

    assert best_pipeline is not None
    assert best_result is not None

    joblib.dump(best_pipeline, model_path)

    metrics_payload = {
        "dataset": dataset_metadata,
        "split": {
            "train_size": int(len(x_train)),
            "validation_size": int(len(x_val)),
            "test_size_fraction": args.test_size,
            "random_state": RANDOM_STATE,
        },
        "candidates": [asdict(result) for result in model_results],
        "best_model": asdict(best_result),
        "saved_model_path": str(model_path),
    }

    with metrics_path.open("w", encoding="utf-8") as output_file:
        json.dump(metrics_payload, output_file, ensure_ascii=False, indent=2)

    print("Training completed.")
    print(f"Best model: {best_result.name}")
    print(f"Validation MAE:  {best_result.mae:.4f}")
    print(f"Validation RMSE: {best_result.rmse:.4f}")
    print(f"Validation R2:   {best_result.r2:.4f}")
    print(f"Model saved to:  {model_path}")
    print(f"Metrics saved to: {metrics_path}")


if __name__ == "__main__":
    main()
