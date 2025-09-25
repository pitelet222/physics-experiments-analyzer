from core.io import read_csv, save_csv, ensure_dir
from core.utils import get_logger
import numpy as np
import pandas as pd
import os
import json
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

class PendulumExperiment:
    name = "pendulum"

    def __init__(self, cfg=None):
        cfg = cfg or {}
        self.g = cfg.get("g", 9.81)
        self.cfg = cfg
        self.logger = get_logger("Pendulum")

    def load(self, path):
        df = read_csv(path)
        # columnas aceptadas case-insensitive: 'longitud' y 'periodo'
        columns = {c.lower(): c for c in df.columns}
        if "longitud" in columns and "periodo" in columns:
            df = df.rename(columns={columns["longitud"]: "Longitud",
                                    columns["periodo"]: "Periodo"})
        else:
            raise ValueError("CSV debe contener columnas 'Longitud' y 'Periodo' (case-insensitive)")
        return df

    def preprocess(self, df):
        df = df.dropna(subset=["Longitud", "Periodo"])
        df["Longitud"] = df["Longitud"].astype(float)
        df["Periodo"] = df["Periodo"].astype(float)
        df["Periodo_teorico"] = 2 * np.pi * np.sqrt(df["Longitud"] / self.g)
        return df

    def analyze(self, df):
        X = np.sqrt(df["Longitud"].values).reshape(-1, 1)
        y = df["Periodo"].values
        model = LinearRegression(fit_intercept=True)
        model.fit(X, y)
        y_pred = model.predict(X)
        slope = float(model.coef_[0])
        intercept = float(model.intercept_)
        mse = float(mean_squared_error(y, y_pred))
        r2 = float(r2_score(y, y_pred))
        expected_slope = 2 * np.pi / np.sqrt(self.g)
        results = {
            "slope": slope,
            "intercept": intercept,
            "mse": mse,
            "r2": r2,
            "expected_slope": expected_slope,
        }
        return results

    def visualize(self, df, out_dir):
        ensure_dir(out_dir)
        plots = []
        # L vs T (medido + teórico)
        fig, ax = plt.subplots()
        ax.scatter(df["Longitud"], df["Periodo"], label="Medido")
        ax.plot(df["Longitud"], df["Periodo_teorico"], label="Teórico", linestyle="--")
        ax.set_xlabel("Longitud (m)")
        ax.set_ylabel("Periodo (s)")
        ax.set_title("Péndulo: Periodo vs Longitud")
        ax.legend()
        p1 = os.path.join(out_dir, "pendulum_L_vs_T.png")
        fig.savefig(p1, dpi=150)
        plt.close(fig)
        plots.append(p1)

        # sqrt(L) vs T con ajuste lineal
        X = np.sqrt(df["Longitud"].values).reshape(-1, 1)
        y = df["Periodo"].values
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        fig2, ax2 = plt.subplots()
        ax2.scatter(np.sqrt(df["Longitud"]), df["Periodo"], label="Medido")
        ax2.plot(np.sqrt(df["Longitud"]), y_pred, label="Ajuste lineal")
        ax2.set_xlabel("sqrt(Longitud) (m^0.5)")
        ax2.set_ylabel("Periodo (s)")
        ax2.set_title("Ajuste T = a * sqrt(L) + b")
        ax2.legend()
        p2 = os.path.join(out_dir, "pendulum_regression.png")
        fig2.savefig(p2, dpi=150)
        plt.close(fig2)
        plots.append(p2)

        return plots

    def export_results(self, results, out_dir):
        ensure_dir(out_dir)
        with open(os.path.join(out_dir, "pendulum_results.json"), "w") as f:
            json.dump(results, f, indent=2)
