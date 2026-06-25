# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.2
#   kernelspec:
#     display_name: all39-defaults
#     language: python
#     name: all39-defaults
# ---

# %% [markdown]
# # Test Plotly
#
# c.f. <https://plotly.com/python/getting-started/#jupyter-notebook-support>

# %%
import holoviews as hv
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# %%
fig = go.Figure(data=go.Bar(y=[2, 3, 1]))
fig.show()

# %%
fig = go.FigureWidget(data=go.Bar(y=[2, 3, 1]))
fig

# %% [markdown]
# # Test Holoview and bokeh

# %%
hv.extension("bokeh")

# %%
df = pd.DataFrame(np.random.randn(10, 2), columns=["x", "y"])

# %%
scatter = hv.Scatter(df, "x", "y")

# %%
scatter
