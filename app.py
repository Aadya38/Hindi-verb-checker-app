# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ---- Load CSV files ----
df = pd.read_csv("merged_verbs.csv", sep=",")
df_plot = pd.read_csv("output_with_root_length.csv")

# ---- Preprocess mapping ----
form_to_row = {}
for _, row in df.iterrows():
    forms = str(row['root']).split(',')
    for form in forms:
        form = form.strip()
        form_to_row[form] = row
    if pd.notnull(row['romanized']):
        form_to_row[row['romanized'].strip().lower()] = row

# ---- Stats ----
df_no_v = df_plot[df_plot["root"].str.strip().str.lower() != "v"]

longest = df_plot.loc[df_plot["root_length"].idxmax()]
shortest = df_no_v.loc[df_no_v["root_length"].idxmin()]  # excludes "v"
avg_length = df_plot["root_length"].mean()
total_verbs = len(df_plot)

# ---- Page Config ----
st.set_page_config(page_title="Hindi Verb Info Checker", page_icon="📚", layout="wide")

# ---- Sidebar Navigation ----
page = st.sidebar.radio("📌 Navigate", ["Home", "Fun facts about Hindi verbs", "Top 20 Hindi Verbs"])

# ---- Home ----
if page == "Home":
    st.title("📖 Hindi Verb Info Checker")
    st.markdown("""
    <div style="background-color:#f9f9f9; color:#000000; padding:10px; border-radius:10px;">
    <b>Check if your favourite Hindi Verb is in our list. Get info about its frequency and forms.</b>
    </div>
    """, unsafe_allow_html=True)

    user_input = st.text_input("🔍 Enter a Hindi verb (Devanagari or Romanized):")

    if user_input:
        user_input_clean = user_input.strip()

        # Try exact Devanagari match first
        row = form_to_row.get(user_input_clean)
        # If not found, try romanized lowercased
        if row is None:
            row = form_to_row.get(user_input_clean.lower())

        st.progress(50)

        if row is not None and isinstance(row, pd.Series):
            st.success(f"✅ '{user_input}' is found!")
            st.markdown(f"**Root:** {row['root']}")
            st.markdown(f"**Verb Forms:** {row['verb_forms']}")
            st.markdown(f"**Count of Verb Forms:** {row['count_vf']}")
            st.markdown(f"**Frequency:** {row['frequency']}")
            st.markdown(f"**English Gloss (romanized):** {row['romanized']}")
            st.balloons()
        else:
            st.error(f"❌ '{user_input}' is NOT found in the verb forms.")

    st.markdown("""
    <div style="background-color:#e8f0fe; color:#000000; padding:10px; border-radius:10px;">
    If your verb is not in our list, submit it here:
    <a href="https://docs.google.com/document/d/1F3x4JV6eZ6Od3psyjmQwo_XPvpDZ-KHvO0ns7JEL5eI/edit?usp=sharing" target="_blank">📄 Submit a Verb</a>.
    </div>
    """, unsafe_allow_html=True)

# ---- Stats ----
elif page == "Fun facts about Hindi verbs":
    st.title("📊 Verb Statistics & Fun Facts")

    st.markdown(f"- 📏 Longest verb: **{longest['root']}** (length {longest['root_length']})")
    st.markdown(f"- 🪶 Shortest verb: **{shortest['root']}** (length {shortest['root_length']})")
    st.markdown(f"- 📐 Average verb length: **{avg_length:.2f}**")
    st.markdown(f"- 📚 Total verbs: **{total_verbs}**")

    if st.button("Show Distribution of Verb Lengths"):
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(df_plot["root_length"], bins=range(1, df_plot["root_length"].max() + 2),
                color='skyblue', edgecolor='black')
        ax.set_xlabel("Root Length")
        ax.set_ylabel("Number of Verbs")
        ax.set_title("Distribution of Verb Lengths")
        st.pyplot(fig)

    if st.button("Show Frequency vs Root Length"):
        fig1, ax1 = plt.subplots(figsize=(8, 6))
        ax1.scatter(df_plot["root_length"], df_plot["frequency"],
                    color='royalblue', alpha=0.7, edgecolors='w', s=80)
        ax1.set_xlabel("Root Length")
        ax1.set_ylabel("Frequency")
        ax1.set_title("Frequency vs Root Length")
        ax1.grid(True)
        st.pyplot(fig1)

    if st.button("Show Zipf's Law Plot"):
        df_sorted = df_plot.sort_values(by="frequency", ascending=False).reset_index(drop=True)
        df_sorted["rank"] = df_sorted.index + 1
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        ax2.plot(np.log10(df_sorted["rank"]), np.log10(df_sorted["frequency"]),
                 marker='o', linestyle='None', color='darkorange')
        ax2.set_xlabel("log10(Rank)")
        ax2.set_ylabel("log10(Frequency)")
        ax2.set_title("Zipf's Law: log(Rank) vs log(Frequency)")
        ax2.grid(True)
        st.pyplot(fig2)

# ---- Top 20 ----
elif page == "Top 20 Hindi Verbs":
    st.title("🏆 Top 20 Verbs by Frequency")

    df_sorted = df_plot.sort_values(by="frequency", ascending=False).head(20)
    st.dataframe(df_sorted[["root", "frequency", "root_length"]])

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(df_sorted["romanized"], df_sorted["frequency"], color='lightgreen')
    ax.invert_yaxis()
    ax.set_xlabel("Frequency")
    ax.set_title("Top 20 Verbs by Frequency")
    st.pyplot(fig)
