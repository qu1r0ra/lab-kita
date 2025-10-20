import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import config  

@st.cache_resource  
def get_db_connection():
    """Create a database connection"""
    try:
        conn = mysql.connector.connect(**config.DB_CONFIG['warehouse'])
        print("Database connection successful")
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        st.error(f"Error connecting to database: {e}")
        return None

def fetch_query(query, params=None):
    """Run a query and return a DataFrame"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            data = cursor.fetchall()
            cursor.close()
            
            return pd.DataFrame(data)
        except Error as e:
            st.error(f"SQL Error: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data
def get_filter_options():
    airlines = fetch_query("SELECT DISTINCT airline_name FROM dim_airline ORDER BY airline_name")
    origins = fetch_query("SELECT DISTINCT origin_city FROM dim_route ORDER BY origin_city")
    destinations = fetch_query("SELECT DISTINCT destination_city FROM dim_route ORDER BY destination_city")
    classes = fetch_query("SELECT DISTINCT flight_class FROM dim_flight ORDER BY flight_class")
    return airlines['airline_name'], origins['origin_city'], destinations['destination_city'], classes['flight_class']

st.set_page_config(layout="wide")
st.title("✈️ Flight Data Warehouse - OLAP Application")

airline_options, origin_options, destination_options, class_options = get_filter_options()

st.header("1. Airline Performance (Slice)")
st.write("Select a single airline to see its average performance metrics.")

selected_airline_slice = st.selectbox("Select Airline:", airline_options, key="slice_airline")

if selected_airline_slice:
    slice_query = """
        SELECT
            da.airline_name,
            AVG(ffm.flight_price) AS 'Average Price',
            AVG(ffm.flight_duration) AS 'Average Duration (hrs)',
            AVG(ffm.flight_stops) AS 'Average Stops'
        FROM fact_flight_metrics ffm
        JOIN dim_airline da ON ffm.airline_key = da.airline_key
        WHERE da.airline_name = %s
        GROUP BY da.airline_name;
    """
    slice_data = fetch_query(slice_query, (selected_airline_slice,))
    st.dataframe(slice_data)

st.header("2. Specific Route Analyzer (Dice)")
st.write("Filter by origin, destination, and class to find average prices.")

col1, col2, col3 = st.columns(3)
with col1:
    selected_origin = st.selectbox("Select Origin City:", origin_options, key="dice_origin")
with col2:
    selected_destination = st.selectbox("Select Destination City:", destination_options, key="dice_dest")
with col3:
    selected_class = st.selectbox("Select Flight Class:", class_options, key="dice_class")

if selected_origin and selected_destination and selected_class:
    dice_query = """
        SELECT
            dr.origin_city,
            dr.destination_city,
            df.flight_class,
            AVG(ffm.flight_price) AS 'Average Price'
        FROM fact_flight_metrics ffm
        JOIN dim_route dr ON ffm.route_key = dr.route_key
        JOIN dim_flight df ON ffm.flight_key = df.flight_key
        WHERE
            dr.origin_city = %s
            AND dr.destination_city = %s
            AND df.flight_class = %s
        GROUP BY
            dr.origin_city, dr.destination_city, df.flight_class;
    """
    dice_data = fetch_query(dice_query, (selected_origin, selected_destination, selected_class))
    st.dataframe(dice_data)

st.header("3. Airline Complaint Analysis (Roll-Up & Drill-Down)")
st.write("View rolled-up complaint data, then select an airline to drill down into yearly details.")

st.subheader("Roll-Up: Average Complaints by Airline (All Time)")
rollup_query = """
    SELECT
        da.airline_name,
        AVG(fcm.complaints_per_million) AS 'Avg Complaints per Million'
    FROM fact_complaint_metrics fcm
    JOIN dim_airline da ON fcm.airline_key = da.airline_key
    GROUP BY da.airline_name
    ORDER BY 2 DESC;
"""
rollup_data = fetch_query(rollup_query)
st.bar_chart(rollup_data.set_index('airline_name'))

st.subheader("Drill-Down: Yearly Complaints for a Specific Airline")
selected_airline_drill = st.selectbox("Select Airline to Drill Down:", airline_options, key="drill_airline")

if selected_airline_drill:
    
    drilldown_query = """
        SELECT
            da.airline_name,
            fcm.date_year,
            AVG(fcm.complaints_per_million) AS 'Complaints per Million'
        FROM fact_complaint_metrics fcm
        JOIN dim_airline da ON fcm.airline_key = da.airline_key
        WHERE da.airline_name = %s
        GROUP BY da.airline_name, fcm.date_year
        ORDER BY fcm.date_year;
    """
    
    drilldown_data = fetch_query(drilldown_query, (selected_airline_drill,))
    
    if not drilldown_data.empty:
        
        chart_data = pd.DataFrame({
            'date_year': drilldown_data['date_year'].astype(str),
            'Complaints per Million': drilldown_data['Complaints per Million']
        })

        st.line_chart(chart_data, x='date_year', y='Complaints per Million')
        
    else:
        st.write("No complaint data found for this airline.")