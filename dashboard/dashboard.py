import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib
from babel.numbers import format_currency
from func import DataAnalyzer, BrazilMapPlotter

sns.set(style='darkgrid')
# st.set_option('deprecation.showPyplotGlobalUse', False)

# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv("dashboard/main_data.csv")
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

# Geolocation Dataset
geolocation = pd.read_csv('dashboard/geolocation.csv')
data = geolocation.drop_duplicates(subset='customer_unique_id')

for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Sidebar
with st.sidebar:
    # Title
    st.title("Elluy Gabriel Panambe")
    
    # Menambahkan logo perusahaan
    st.image("dashboard/streamlit-seeklogo.svg", width=200)
    
    # Informasi tanggal
    st.write(f"Data from: **{min_date.date()}** to **{max_date.date()}**")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Main
main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                 (all_df["order_approved_at"] <= str(end_date))]

function = DataAnalyzer(main_df)
map_plot = BrazilMapPlotter(data, plt, mpimg, urllib, st)

# Analisis Data
daily_orders_df = function.create_daily_orders_df()
sum_order_items_df = function.create_sum_order_items_df()
state, most_common_state = function.create_bystate_df()
order_status, common_status = function.create_order_status()
rfm_df = DataAnalyzer(all_df).create_rfm_df()

# Title
st.header("E-Commerce Data Analysis Dashboard")

st.write("**Interactive analysis of public e-commerce data**")

# Daily Orders
st.subheader("📅 Daily Orders")

col1, col2 = st.columns(2)
with col1:
    total_order = daily_orders_df["order_count"].sum()
    st.metric(label="Total Orders", value=f"{total_order}")

with col2:
    total_revenue = format_currency(daily_orders_df["revenue"].sum(), "IDR", locale="id_ID")
    st.metric(label="Total Revenue", value=f"{total_revenue}")

# Visualisasi Daily Orders
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.set_title("Order Trend Over Time", fontsize=16)
ax.tick_params(axis="x", rotation=45)
st.pyplot(fig)

# Order Items
st.subheader("🔝 Best & Worst Performing Products")

col1, col2 = st.columns(2)
with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.metric(label="Total Items Sold", value=f"{total_items}")

with col2:
    avg_items = round(sum_order_items_df["product_count"].mean(), 2)
    st.metric(label="Average Items Sold", value=f"{avg_items}")

# Visualisasi Best & Worst Products
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))
colors = ["#068DA9", "#FFA07A", "#8FBC8F", "#D3D3D3", "#FFD700"]

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.head(5), palette="viridis", ax=ax[0], legend=False)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=80)
ax[0].set_title("Most sold products", loc="center", fontsize=90)
ax[0].tick_params(axis ='y', labelsize=55)
ax[0].tick_params(axis ='x', labelsize=50)

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), palette="viridis", ax=ax[1], legend=False)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=80)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Fewest products sold", loc="center", fontsize=90)
ax[1].tick_params(axis='y', labelsize=55)
ax[1].tick_params(axis='x', labelsize=50)

st.pyplot(fig)

# Customer Demographics
st.subheader("👥 Customer Demographics")

tab1, tab2, tab3 = st.tabs(["State", "Order Status", "Geolocation"])

with tab1:
    most_common_state = state.customer_state.value_counts().index[0]
    st.metric(label="Most Common State", value=f"{most_common_state}")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=state.customer_state.value_counts().index, 
                y=state.customer_count.values, 
                palette=["#068DA9" if score == most_common_state else "#D3D3D3" for score in state.customer_state.value_counts().index], ax=ax, legend=False)
    ax.set_title("Number of Customers by State", fontsize=15)
    st.pyplot(fig)

with tab2:
    common_status_ = order_status.value_counts().index[0]
    st.metric(label="Most Common Order Status", value=f"{common_status_}")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=order_status.index, y=order_status.values, 
                palette=["#068DA9" if score == common_status else "#D3D3D3" for score in order_status.index], ax=ax, legend=False)
    ax.set_title("Order Status Distribution", fontsize=15)
    st.pyplot(fig)

with tab3:
    map_plot.plot()
    with st.expander("See Explanation"):
        st.write("Most customers are from the southeastern and southern regions, particularly in major cities like São Paulo and Rio de Janeiro.")

# Best Customer Based on RFM
st.subheader("🏆 Best Customers by RFM Analysis")

col1, col2, col3 = st.columns(3)
with col1:
    avg_recency = round(rfm_df['Recency'].mean(), 1)
    st.metric(label="Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df['Frequency'].mean(), 2)
    st.metric(label="Average Frequency", value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_df['Monetary'].mean(), "IDR", locale="id_ID")
    st.metric(label="Average Monetary", value=avg_monetary)

# RFM Visualization
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(25, 8))
colors = ["#90CAF9"] * 5

# Shorten customer IDs for display
rfm_df['short_customer_id'] = rfm_df['customer_id'].astype(str).str[-5:]  # Keep only last 5 digits

sns.barplot(y="Recency", x="short_customer_id", data=rfm_df.sort_values(by="Recency").head(5), palette=colors, ax=ax[0], legend=False)
ax[0].set_title("Top 5 by Recency", fontsize=15)

sns.barplot(y="Frequency", x="short_customer_id", data=rfm_df.sort_values(by="Frequency", ascending=False).head(5), palette=colors, ax=ax[1], legend=False)
ax[1].set_title("Top 5 by Frequency", fontsize=15)

sns.barplot(y="Monetary", x="short_customer_id", data=rfm_df.sort_values(by="Monetary", ascending=False).head(5), palette=colors, ax=ax[2], legend=False)
ax[2].set_title("Top 5 by Monetary", fontsize=15)

st.pyplot(fig)

st.caption('© Elluy Gabriel Panambe 2024')