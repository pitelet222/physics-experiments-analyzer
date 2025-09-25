import pandas as pd
from experiments.pendulum import PendulumExperiment

def test_preprocess_adds_periodo_teorico():
    exp = PendulumExperiment({})
    df = pd.DataFrame({"Longitud":[0.1, 0.5],"Periodo":[0.63,1.4]})
    df2 = exp.preprocess(df.copy())
    assert "Periodo_teorico" in df2.columns
    assert df2["Periodo_teorico"].dtype == float
