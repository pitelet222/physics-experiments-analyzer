#!/usr/bin/env python3
import argparse
import yaml
from importlib import import_module
from core.io import ensure_dir
from core.utils import get_logger

logger = get_logger("main")

def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def load_plugin(experiment_name):
    module_name = f"experiments.{experiment_name}"
    mod = import_module(module_name)
    # buscar una clase que termine en 'Experiment'
    for attr in dir(mod):
        obj = getattr(mod, attr)
        if isinstance(obj, type) and attr.lower().endswith("experiment"):
            return obj
    raise ImportError(f"No '...Experiment' class found in {module_name}")

def main():
    parser = argparse.ArgumentParser(description="Analizador genérico de experimentos físicos")
    parser.add_argument("--experiment", required=True, help="Nombre del experimento (ej: pendulum)")
    parser.add_argument("--input", required=True, help="CSV de entrada")
    parser.add_argument("--config", default="config/default_config.yml", help="Archivo de configuración YAML")
    parser.add_argument("--out", default=None, help="Directorio de salida (opcional)")
    args = parser.parse_args()

    cfg = load_config(args.config)
    out_dir = args.out or cfg.get("general", {}).get("output_dir", "outputs")
    ensure_dir(out_dir)

    plugin_class = load_plugin(args.experiment.lower())
    plugin_cfg = cfg.get(args.experiment.lower(), {})
    exp = plugin_class(plugin_cfg)

    logger.info("Cargando datos...")
    df = exp.load(args.input)
    logger.info("Preprocesando...")
    df = exp.preprocess(df)
    logger.info("Analizando...")
    results = exp.analyze(df)
    logger.info("Visualizando y guardando...")
    plots = exp.visualize(df, out_dir)
    exp.export_results(results, out_dir)
    logger.info(f"Hecho. Resultados: {out_dir}")

if __name__ == "__main__":
    main()
