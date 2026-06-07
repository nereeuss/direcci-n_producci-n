import pandas as pd
import numpy as np

class Previsionador:
    def __init__(self, serie_datos):
        # Limpiamos y aseguramos que trabajamos con números
        self.data = serie_datos.dropna().reset_index(drop=True)
    
    def media_movil_excel(self, k):
        dt = self.data.values
        n = len(dt)
        pt = np.full(n, np.nan) 
        
        # El pronóstico es la media de los últimos k periodos
        pron_futuro = np.mean(dt[-k:])
        
        # Asignamos este pronóstico a los últimos k periodos para calcular su error
        for t in range(n - k, n):
            pt[t] = pron_futuro
            
        return pd.Series(pt), pron_futuro
    
    def media_movil_ponderada_excel(self, pesos):
        dt = self.data.values
        n = len(dt)
        k = len(pesos)
        pt = np.full(n, np.nan)
        
        # Invertimos los pesos para que W1 sea el más antiguo y Wk el más reciente
        # o según como los estés ingresando.
        pesos_arr = np.array(pesos)
        
        for t in range(k, n):
            # Multiplicamos los k datos anteriores por los pesos
            ventana = dt[t-k:t]
            pt[t] = np.sum(ventana * pesos_arr)
            
        # Pronóstico para el periodo N+1
        pron_futuro = np.sum(dt[-k:] * pesos_arr)
        
        return pd.Series(pt), pron_futuro

    def alisado_simple_excel(self, alpha):
        dt = self.data.values
        at = np.zeros(len(dt))
        # Semilla: at1 = dt1
        at[0] = dt[0] 
        for t in range(1, len(dt)):
            at[t] = at[t-1] + alpha * (dt[t-1] - at[t-1])
        # Devuelve 3 valores para que app.py no de error
        return pd.Series(at), None, pd.Series(at)

    def alisado_doble_excel(self, alpha, beta):
        dt = self.data.values
        at = np.zeros(len(dt))
        bt = np.zeros(len(dt))
        pt = np.zeros(len(dt))
        # Semilla: at1 = dt1, bt1 = 0
        at[0], bt[0], pt[0] = dt[0], 0, dt[0]
        for t in range(1, len(dt)):
            at[t] = alpha * dt[t] + (1 - alpha) * (at[t-1] + bt[t-1])
            bt[t] = beta * (at[t] - at[t-1]) + (1 - beta) * bt[t-1]
            pt[t] = at[t-1] + bt[t-1]
        return pd.Series(at), pd.Series(bt), pd.Series(pt)

    def alisado_triple_excel(self, alpha, beta, gamma, L):
        dt = self.data.values
        n = len(dt)
        at, bt, ct, pt = np.zeros(n), np.zeros(n), np.zeros(n + L), np.zeros(n)
        # Inicialización estacionalidad ct en 1.0
        ct[:L] = 1.0
        # Semilla t=1
        at[0], bt[0], ct[L], pt[0] = dt[0], 0, 1.0, dt[0]
        for t in range(1, n):
            idx = t + L
            pt[t] = (at[t-1] + bt[t-1]) * ct[idx - L]
            at[t] = alpha * (dt[t] / ct[idx - L]) + (1 - alpha) * (at[t-1] + bt[t-1])
            bt[t] = beta * (at[t] - at[t-1]) + (1 - beta) * bt[t-1]
            ct[idx] = gamma * (dt[t] / at[t]) + (1 - gamma) * ct[idx - L]
        return pd.Series(at), pd.Series(bt), pd.Series(ct[L:]), pd.Series(pt)

    @staticmethod
    def calcular_metricas_universales(real, pronostico):
        error_completo = real - pronostico
        # Saltamos el Año 1 para el promedio (n-1)
        error_util = error_completo.iloc[1:] 
        n_dinamico = len(error_util)
        if n_dinamico > 0:
            vme = error_util.abs().sum() / n_dinamico
            ecm = (error_util**2).sum() / n_dinamico
        else:
            vme, ecm = 0, 0
        return float(vme), float(ecm), n_dinamico