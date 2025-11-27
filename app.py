import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob

st.set_page_config(
    page_title="Amazon Review Analysis Dashboard",
    layout="wide",
    page_icon="📦"
)

# -----------------------------------
# Load Data
# -----------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(r"E:\ProjectsFinal\Analysis_projects_github\Project3_Amazon Customers Data_Analysis\Reviews.csv", low_memory=False)
    
    # Data Preparation - Remove invalid rows
    df = df[df['HelpfulnessNumerator'] <= df['HelpfulnessDenominator']]
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['UserId','ProfileName','Time','Text'])
    
    # Convert Time to datetime
    df['Time'] = pd.to_datetime(df['Time'], unit='s')
    
    # Calculate review length in words
    df['Text_length'] = df['Text'].astype(str).str.split().apply(len)
    
    # Frequent user logic: users with > 50 reviews
    user_counts = df['UserId'].value_counts()
    df['viewer_type'] = df['UserId'].apply(lambda user: 'Frequent' if user_counts[user] > 50 else 'Not Frequent')
    
    return df

df = load_data()


# -----------------------------------
# Sidebar Navigation
# -----------------------------------
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio(
    "Go to Section:",
    [
        "Home",
        "Score Distribution",
        "Top Users",
        "Product vs Score Analysis",
        "Review Length Analysis",
        "Sentiment Analysis",
        "Insights Summary"
    ]
)

# -------------------------------------------------
# HOME
# -------------------------------------------------
if page == "Home":
    st.title("📦 Amazon Customer Review Analysis Dashboard")
    st.markdown("""
    This dashboard provides deep insights into customer review behavior using Amazon customer data.

    ### 🔍 What you can explore:
    - Frequent vs Non-Frequent Reviewer Behavior  
    - Score (Rating) Distribution for User Groups  
    - Top Users by Products Purchased  
    - Product Rating Comparison  
    - Review Length & Verbosity Analysis  
    - Sentiment Analysis of Reviews
    - Actionable insights for recommendations  

    Use the **left sidebar** to navigate between sections.
    """)


# -------------------------------------------------
# SCORE DISTRIBUTION
# -------------------------------------------------
elif page == "Score Distribution":
    st.title("⭐ Score Distribution Analysis")
    st.write("### Frequent vs Non-Frequent Reviewers")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Frequent Users Score Distribution")
        freq_df = df[df['viewer_type'] == 'Frequent']
        score_counts = freq_df['Score'].value_counts().sort_index()
        score_pct = (score_counts / len(freq_df) * 100).round(2)

        fig, ax = plt.subplots()
        ax.bar(score_counts.index, score_counts.values, color="royalblue")
        ax.set_xlabel("Score")
        ax.set_ylabel("Count")
        ax.set_title("Frequent Users Score Distribution")
        st.pyplot(fig)
        
        st.write(score_pct)

    with col2:
        st.subheader("Non-Frequent Users Score Distribution")
        nonfreq_df = df[df['viewer_type'] == 'Not Frequent']
        score_counts2 = nonfreq_df['Score'].value_counts().sort_index()
        score_pct2 = (score_counts2 / len(nonfreq_df) * 100).round(2)

        fig, ax = plt.subplots()
        ax.bar(score_counts2.index, score_counts2.values, color="darkorange")
        ax.set_xlabel("Score")
        ax.set_ylabel("Count")
        ax.set_title("Not Frequent Users Score Distribution")
        st.pyplot(fig)
        
        st.write(score_pct2)



# -------------------------------------------------
# TOP USERS
# -------------------------------------------------
elif page == "Top Users":
    st.title("👥 Top 10 Users by Number of Products Purchased")

    top_users = df.groupby('UserId')['ProductId'].count().sort_values(ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(len(top_users)), top_users.values, color="seagreen")
    ax.set_xticks(range(len(top_users)))
    ax.set_xticklabels(top_users.index, rotation=45, ha='right')
    ax.set_ylabel("Number of Products Purchased")
    ax.set_title("Top 10 Users by No. of Products Purchased")
    plt.tight_layout()

    st.pyplot(fig)



# -------------------------------------------------
# PRODUCT VS SCORE ANALYSIS
# -------------------------------------------------
elif page == "Product vs Score Analysis":
    st.title("📦 Product vs Score Distribution")

    prod_count = df['ProductId'].value_counts()
    top_products = prod_count[prod_count > 500].index
    filtered = df[df['ProductId'].isin(top_products)]

    st.write(f"### Score Breakdown for Top Products (>500 reviews)")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.countplot(y='ProductId', data=filtered, hue='Score', palette='coolwarm', ax=ax)
    ax.set_ylabel("Product ID")
    ax.set_title("Product vs Score Distribution")

    st.pyplot(fig)



# -------------------------------------------------
# REVIEW LENGTH ANALYSIS
# -------------------------------------------------
elif page == "Review Length Analysis":
    st.title("✍️ Review Length & Verbosity Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Frequent Reviewers")
        fig, ax = plt.subplots()
        ax.boxplot(df[df['viewer_type'] == 'Frequent']['Text_length'].dropna())
        ax.set_ylabel("Review Length (words)")
        ax.set_title("Frequent Reviewers Review Length")
        ax.set_ylim(0, 600)
        st.pyplot(fig)

    with col2:
        st.write("### Non-Frequent Reviewers")
        fig, ax = plt.subplots()
        ax.boxplot(df[df['viewer_type'] == 'Not Frequent']['Text_length'].dropna())
        ax.set_ylabel("Review Length (words)")
        ax.set_title("Non-Frequent Reviewers Review Length")
        ax.set_ylim(0, 600)
        st.pyplot(fig)

    st.markdown("""
    ### 📌 Insight:
    Frequent reviewers tend to write **longer, more detailed reviews** compared to non-frequent reviewers.
    """)



# -------------------------------------------------
# SENTIMENT ANALYSIS
# -------------------------------------------------
elif page == "Sentiment Analysis":
    st.title("💭 Sentiment Analysis of Reviews")
    
    st.write("Analyzing sentiment polarity of review summaries...")
    
    # Sample analysis
    sample = df[0:50000].copy()
    
    @st.cache_data
    def calculate_sentiment():
        polarity = []
        for text in sample['Summary']:
            try:
                polarity.append(TextBlob(str(text)).sentiment.polarity)
            except:
                polarity.append(0)
        return polarity
    
    polarity_scores = calculate_sentiment()
    sample['polarity'] = polarity_scores
    
    sample_negative = sample[sample['polarity'] < 0]
    sample_positive = sample[sample['polarity'] > 0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Sentiment Distribution")
        fig, ax = plt.subplots()
        ax.hist(sample['polarity'], bins=50, color='steelblue', edgecolor='black')
        ax.set_xlabel("Polarity Score")
        ax.set_ylabel("Frequency")
        ax.set_title("Sentiment Polarity Distribution")
        st.pyplot(fig)
    
    with col2:
        st.subheader("📈 Sentiment Breakdown")
        sent_counts = {
            'Positive': len(sample_positive),
            'Negative': len(sample_negative),
            'Neutral': len(sample) - len(sample_positive) - len(sample_negative)
        }
        fig, ax = plt.subplots()
        ax.pie(sent_counts.values(), labels=sent_counts.keys(), autopct='%1.1f%%', colors=['green', 'red', 'gray'])
        ax.set_title("Sentiment Distribution")
        st.pyplot(fig)
    
    st.write(f"**Total Reviews Analyzed:** {len(sample):,}")
    st.write(f"**Positive Sentiments:** {len(sample_positive):,}")
    st.write(f"**Negative Sentiments:** {len(sample_negative):,}")



# -------------------------------------------------
# INSIGHTS SUMMARY
# -------------------------------------------------
elif page == "Insights Summary":
    st.title("📌 Key Business Insights Summary")

    st.markdown("""
    ## 1️⃣ Who should Amazon recommend more products to?
    **Frequent users** (>50 reviews) – they show:
    - Higher engagement and purchase frequency  
    - Consistent reviewing patterns  
    - More detailed, valuable feedback  
    - Better indicators of product quality  

    ---

    ## 2️⃣ Behavioral differences between frequent & non-frequent users
    | Frequent Users | Non-Frequent Users |
    |----------------|--------------------|
    | Very positive ratings | Mixed ratings |
    | Many purchases | Few purchases |
    | Long, detailed reviews | Short reviews |
    | Consistent engagement | Irregular engagement |

    **Frequent users are valuable, loyal, repeat purchasers.**

    ---

    ## 3️⃣ Are frequent users more verbose?
    ✔ **Yes.**  
    Frequent users write **longer, more descriptive reviews** than non-frequent users.

    This makes their feedback more valuable for:
    - NLP sentiment analysis  
    - Product improvement insights  
    - Personalized recommendation systems  

    ---
    
    ## 4️⃣ Sentiment Insights
    - Review polarity helps identify product quality  
    - Negative reviews highlight pain points  
    - Positive reviews from frequent users are highly reliable  

    ---
    ### 🎯 Final Recommendation
    Amazon should:
    - **Prioritize frequent reviewers** for targeted product offers  
    - Use their **detailed feedback** for product optimization  
    - Build **segmentation models** based on review frequency  
    - Focus on **sentiment analysis** to identify product issues early  
    - **Incentivize frequent reviewers** to maintain engagement  
    """)

