# app.py — Single page Plotly Dashboard (no dropdown)
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
from textblob import TextBlob

st.set_page_config(page_title="Amazon Review Analysis (Plotly)", layout="wide", page_icon="📦")

# -----------------------
# Load & prepare data
# -----------------------
@st.cache_data
def load_data(path=r"E:\ProjectsFinal\Analysis_projects_github\Project3_Amazon Customers Data_Analysis\Reviews.csv"):
    df = pd.read_csv(path, low_memory=False)

    # Basic cleaning from your app
    df = df[df['HelpfulnessNumerator'] <= df['HelpfulnessDenominator']]
    df = df.drop_duplicates(subset=['UserId', 'ProfileName', 'Time', 'Text'])
    df['Time'] = pd.to_datetime(df['Time'], unit='s')
    df['Text_length'] = df['Text'].astype(str).str.split().apply(len)

    user_counts = df['UserId'].value_counts()
    df['viewer_type'] = df['UserId'].apply(lambda user: 'Frequent' if user_counts[user] > 50 else 'Not Frequent')

    return df

df = load_data()  # change path if needed

# -----------------------
# Page Title + Intro
# -----------------------
st.title("📦 Amazon Customer Review Analysis (Plotly)")
st.markdown(
    """
Single-page interactive dashboard (Plotly) showing reviewer behavior, product rating trends, review verbosity and sentiment analysis.
- All visuals are interactive (hover / zoom).
- No dropdowns — scroll to navigate sections.
"""
)

# -----------------------
# Section: Score Distribution
# -----------------------
st.header("⭐ Score Distribution — Frequent vs Not Frequent")

freq = df[df['viewer_type'] == 'Frequent']
notfreq = df[df['viewer_type'] == 'Not Frequent']

# build aggregated counts
score_freq = freq['Score'].value_counts().sort_index().rename_axis('Score').reset_index(name='Count')
score_notfreq = notfreq['Score'].value_counts().sort_index().rename_axis('Score').reset_index(name='Count')

col1, col2 = st.columns(2)
with col1:
    fig_freq = px.bar(score_freq, x='Score', y='Count', title='Frequent Users — Score Distribution',
                      labels={'Count':'Count','Score':'Score'}, height=400)
    st.plotly_chart(fig_freq, use_container_width=True)

    # percent table
    pct = (score_freq.set_index('Score')['Count'] / score_freq['Count'].sum() * 100).round(2)
    st.write("Percent distribution (Frequent):")
    st.dataframe(pct.rename("Percent (%)"))

with col2:
    fig_not = px.bar(score_notfreq, x='Score', y='Count', title='Not Frequent Users — Score Distribution',
                     labels={'Count':'Count','Score':'Score'}, height=400)
    st.plotly_chart(fig_not, use_container_width=True)

    pct2 = (score_notfreq.set_index('Score')['Count'] / score_notfreq['Count'].sum() * 100).round(2)
    st.write("Percent distribution (Not Frequent):")
    st.dataframe(pct2.rename("Percent (%)"))

st.markdown("---")

# -----------------------
# Section: Top Users
# -----------------------
st.header("👥 Top 10 Users by Number of Products Purchased")
top_users = df.groupby('UserId')['ProductId'].count().sort_values(ascending=False).head(10).reset_index()
top_users.columns = ['UserId', 'Products_Purchased']
fig_top = px.bar(top_users, x='UserId', y='Products_Purchased', title='Top 10 Active Users',
                 labels={'Products_Purchased':'# Products Reviewed', 'UserId':'UserId'}, height=450)
fig_top.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_top, use_container_width=True)

st.markdown("---")

# -----------------------
# Section: Product vs Score Analysis (Top products only)
# -----------------------
st.header("📦 Product vs Score Analysis (Products with > 500 reviews)")

prod_count = df['ProductId'].value_counts()
top_products = prod_count[prod_count > 500].index
filtered = df[df['ProductId'].isin(top_products)].copy()

if filtered.empty:
    st.info("No products found with > 500 reviews in the dataset. Adjust threshold or check dataset.")
else:
    # Use histogram / countplot style in Plotly
    # We'll aggregate counts per ProductId and Score for stacked bar (horizontal)
    agg = filtered.groupby(['ProductId', 'Score']).size().reset_index(name='Count')
    # show only top N products for readability
    topN = agg['ProductId'].value_counts().head(20).index  # limit to top 20 product ids in that filtered set
    agg_top = agg[agg['ProductId'].isin(topN)]

    fig_prod = px.bar(agg_top, y='ProductId', x='Count', color='Score',
                      orientation='h',
                      title='Product vs Score Distribution (Top products)',
                      labels={'Count':'Count', 'ProductId':'ProductId'},
                      height=700)
    st.plotly_chart(fig_prod, use_container_width=True)

st.markdown("---")

# -----------------------
# Section: Review Length Analysis
# -----------------------
st.header("✍️ Review Length & Verbosity Analysis")

fig_box = px.box(df, x='viewer_type', y='Text_length',
                 labels={'viewer_type':'Viewer Type', 'Text_length':'Review Length (words)'},
                 title='Review Length by Viewer Type', points='outliers', height=450)
fig_box.update_yaxes(range=[0, 600])
st.plotly_chart(fig_box, use_container_width=True)

st.markdown("""
**Insight:** Frequent reviewers typically write longer reviews — more useful for product feedback and NLP tasks.
""")
st.markdown("---")

# -----------------------
# Section: Sentiment Analysis (matches Jupyter notebook)
# -----------------------
st.header("💬 Sentiment Analysis (TextBlob) — Sample of 50,000 summaries")

# Ensure Summary column exists — if not, try 'Text' as fallback
text_col = 'Summary' if 'Summary' in df.columns else 'Text'

sample = df.head(50000).copy()[[text_col]].rename(columns={text_col: 'Summary'})
sample['Summary'] = sample['Summary'].astype(str)

@st.cache_data
def compute_polarity(series):
    # vectorized-like loop but cached
    polarity = []
    for txt in series:
        try:
            polarity.append(TextBlob(txt).sentiment.polarity)
        except:
            polarity.append(0.0)
    return polarity

sample['polarity'] = compute_polarity(sample['Summary'])

# categorize
sample['sentiment'] = sample['polarity'].apply(lambda x: 'Positive' if x > 0 else ('Negative' if x < 0 else 'Neutral'))

pos = (sample['sentiment'] == 'Positive').sum()
neg = (sample['sentiment'] == 'Negative').sum()
neu = (sample['sentiment'] == 'Neutral').sum()

col1, col2 = st.columns([2,1])
with col1:
    fig_hist = px.histogram(sample, x='polarity', nbins=50, title='Sentiment Polarity Distribution (Sample)',
                            labels={'polarity':'Polarity Score', 'count':'Frequency'}, height=400)
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    fig_pie = px.pie(names=['Positive','Negative','Neutral'], values=[pos, neg, neu],
                     title='Sentiment Breakdown', height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

st.write(f"Total reviews analyzed (sample): {len(sample):,}")
st.write(f"Positive: {pos:,}, Negative: {neg:,}, Neutral: {neu:,}")

st.markdown("---")

# -----------------------
# Section: Insights Summary
# -----------------------
st.header("📌 Key Business Insights Summary")

st.markdown("""
### 1️⃣ Who should Amazon recommend more products to?
**Frequent users** (>50 reviews) — they show:
- Higher engagement and purchase frequency
- Consistent reviewing patterns
- More detailed, valuable feedback
- Better indicators of product quality

---

### 2️⃣ Behavioral differences between frequent & non-frequent users
| Frequent Users | Non-Frequent Users |
|----------------|--------------------|
| Very positive ratings | Mixed ratings |
| Many purchases | Few purchases |
| Long, detailed reviews | Short reviews |
| Consistent engagement | Irregular engagement |

**Frequent users are valuable, loyal, repeat purchasers.**

---

### 3️⃣ Are frequent users more verbose?
✔ **Yes.** Frequent users write longer, more descriptive reviews.

---

### 4️⃣ Quick Recommendations
- Prioritize frequent reviewers for targeted offers and early product feedback.
- Use long-form reviews to train product-quality models and extract improvement suggestions.
- Use product-level rating distributions to flag underperforming items.
""")

st.markdown("---")
st.caption("Built with Streamlit + Plotly · Data cleaning & logic derived from your original app. :contentReference[oaicite:1]{index=1}")