import streamlit as st
import pandas as pd
import numpy as np

st.markdown("# Hello world!!!")

df: pd.DataFrame = pd.DataFrame(
    np.random.randn(30, 3),
    columns=["x", "y", "z"]
)
st.line_chart(df)