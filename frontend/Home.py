import plotly.express as px
import streamlit as st

from backend.db import get_engine
from frontend.ui.ui_framework.common import page_setup
from frontend.ui.ui_framework.data_access import read_sql_with_recovery

page_setup(title="Reptile Central", icon=":lizard:")

st.title("Reptile Central Database Manager")
st.write("View and manage animals, products, customers, orders, and employees.")

try:
    engine = get_engine()

    animals_df     = read_sql_with_recovery(engine, "SELECT COUNT(*) AS n FROM Animals WHERE isAvailable = 1;")
    customers_df   = read_sql_with_recovery(engine, "SELECT COUNT(*) AS n FROM Customers;")
    orders_df      = read_sql_with_recovery(engine, "SELECT COUNT(*) AS n FROM Orders;")
    revenue_df     = read_sql_with_recovery(engine, "SELECT COALESCE(SUM(orderTotal), 0) AS n FROM Orders;")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Animals Available", int(animals_df["n"].iloc[0]))
    col2.metric("Total Customers",   int(customers_df["n"].iloc[0]))
    col3.metric("Total Orders",      int(orders_df["n"].iloc[0]))
    col4.metric("Total Revenue",     f"${float(revenue_df['n'].iloc[0]):,.2f}")

    st.markdown("---")

    revenue_by_month = read_sql_with_recovery(
        engine,
        "SELECT DATE_FORMAT(orderDate, '%%Y-%%m') AS month, SUM(orderTotal) AS revenue "
        "FROM Orders GROUP BY month ORDER BY month;",
    )
    species_counts = read_sql_with_recovery(
        engine,
        "SELECT species, COUNT(*) AS count FROM Animals WHERE isAvailable = 0 AND orderID IS NOT NULL "
        "GROUP BY species ORDER BY count DESC;",
    )
    top_products = read_sql_with_recovery(
        engine,
        "SELECT p.productName, SUM(od.quantity) AS units_sold "
        "FROM OrderDetails od "
        "JOIN Products p ON od.productID = p.productID "
        "JOIN Orders o ON od.orderID = o.orderID "
        "WHERE MONTH(o.orderDate) = MONTH(CURDATE()) AND YEAR(o.orderDate) = YEAR(CURDATE()) "
        "GROUP BY p.productName ORDER BY units_sold DESC LIMIT 8;",
    )

    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.subheader("Revenue by Month")
        fig = px.line(
            revenue_by_month, x="month", y="revenue",
            labels={"month": "", "revenue": "Revenue ($)"},
            markers=True,
        )
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300)
        st.plotly_chart(fig, use_container_width=True)

    with chart_right:
        st.subheader("Animals Sold by Species")
        if species_counts.empty:
            st.caption("No animals sold yet.")
        else:
            fig = px.bar(
                species_counts, x="count", y="species",
                orientation="h",
                labels={"count": "Sold", "species": ""},
            )
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top Products This Month")
    if top_products.empty:
        st.caption("No product orders recorded this month.")
    else:
        fig = px.bar(
            top_products, x="productName", y="units_sold",
            labels={"productName": "", "units_sold": "Units Sold"},
            color="units_sold",
            color_continuous_scale="Greens",
        )
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

except Exception as exc:
    st.warning(f"Could not load dashboard: {exc}")
