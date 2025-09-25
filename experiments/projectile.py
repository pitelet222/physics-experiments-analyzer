import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import json

from core.io import read_csv, ensure_dir
from core.utils import get_logger

class ProjectileExperiment:
    name = "projectile"

    def __init__(self, cfg=None):
        cfg = cfg or {}
        self.g = cfg.get("g", 9.81)
        self.logger = get_logger("Projectile")

    def load(self, path):
        df = read_csv(path)
        expected = {"Tiempo", "X", "Y"}
        if not expected.issubset(set(df.columns)):
            raise ValueError(f"CSV debe contener columnas {expected}")
        return df

    def preprocess(self, df):
        df = df.dropna(subset=["Tiempo", "X", "Y"])
        df["Tiempo"] = df["Tiempo"].astype(float)
        df["X"] = df["X"].astype(float)
        df["Y"] = df["Y"].astype(float)
        return df

    def analyze(self, df):
        dx = df["X"].iloc[-1] - df["X"].iloc[0]
        dt = df["Tiempo"].iloc[-1] - df["Tiempo"].iloc[0]
        vx = dx / dt if dt != 0 else float("nan")
        y_max = df["Y"].max()
        v0y = np.sqrt(2 * self.g * y_max) if y_max > 0 else 0.0
        results = {
            "vx_promedio": float(vx),
            "v0y_estimado": float(v0y),
            "v0_estimado": float(np.sqrt(vx**2 + v0y**2))
        }
        return results

    def visualize(self, df, out_dir):
        ensure_dir(out_dir)
        plots = []
        fig, ax = plt.subplots()
        ax.plot(df["X"], df["Y"], "o-", label="Trayectoria")
        ax.set_xlabel("X (m)")
        ax.set_ylabel("Y (m)")
        ax.set_title("Movimiento parabólico")
        ax.legend()
        p = os.path.join(out_dir, "projectile_trajectory.png")
        fig.savefig(p, dpi=150)
        plt.close(fig)
        plots.append(p)
        return plots

    def export_results(self, results, out_dir):
        ensure_dir(out_dir)
        with open(os.path.join(out_dir, "projectile_results.json"), "w") as f:
            json.dump(results, f, indent=2)
