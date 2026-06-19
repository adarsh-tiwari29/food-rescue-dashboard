import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
import time

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Pro Food Rescue Dashboard", page_icon="🍲", layout="wide")

# --- 2. DATABASE CONNECTION ---
# Streamlit deployment ke liye hum SQLite database file ka use kar rahe hain
engine = create_engine("sqlite:///food_wastage.db")

@st.cache_data
def load_data(query):
    return pd.read_sql(query, engine)

# --- 3. DATA LOADING ---
try:
    df_food = load_data("SELECT * FROM food_listings")
    df_providers = load_data("SELECT * FROM providers")
    df_claims = load_data("SELECT * FROM claims")
    df_receivers = load_data("SELECT * FROM receivers")
except Exception as e:
    st.error(f"Database Connection Failed: {e}")
    st.stop()

# --- 4. SIDEBAR (FILTERS) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3274/3274099.png", width=100)
st.sidebar.title("Filter Options")

cities = df_providers['City'].dropna().unique().tolist()
cities.insert(0, "All")
selected_city = st.sidebar.selectbox("Select City", cities)

provider_types = df_food['Provider_Type'].dropna().unique().tolist()
provider_types.insert(0, "All")
selected_provider = st.sidebar.selectbox("Select Provider Type", provider_types)

# Applying Filters
filtered_food = df_food.copy()
if selected_city != "All":
    filtered_food = filtered_food[filtered_food['Location'] == selected_city]
if selected_provider != "All":
    filtered_food = filtered_food[filtered_food['Provider_Type'] == selected_provider]

# --- 5. MAIN HEADER ---
st.title(" Local Food Wastage Management System")
st.markdown("An advanced analytics and operational dashboard to monitor, manage, and reduce food wastage.")
st.divider()


tab1, tab2, tab3 = st.tabs([" Analytics Hub", " Data Explorer", " Manage Data (CRUD)"])


# TAB 1: ANALYTICS HUB (CHARTS & KPIs)

with tab1:
    # Top KPIs
    st.markdown("###  Real-time KPIs")
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.metric(label="Total Active Listings", value=len(filtered_food))
    with kpi2:
        st.metric(label="Total Volume (Qty)", value=int(filtered_food['Quantity'].sum()))
    with kpi3:
        st.metric(label="Total Claims Made", value=len(df_claims))
    with kpi4:
        success_rate = round((len(df_claims[df_claims['Status'] == 'Completed']) / len(df_claims)) * 100, 1) if len(df_claims) > 0 else 0
        st.metric(label="Claim Success Rate", value=f"{success_rate}%")
    with kpi5:
        st.metric(label="Registered Receivers", value=len(df_receivers))

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1 Charts
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        if not filtered_food.empty:
            fig1 = px.pie(filtered_food, names='Provider_Type', values='Quantity', 
                          title='Food Volume by Provider Type', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig1, use_container_width=True)
            
    with col_chart2:
        if not filtered_food.empty:
            fig2 = px.bar(filtered_food.groupby('Meal_Type', as_index=False)['Quantity'].sum(), 
                          x='Meal_Type', y='Quantity', color='Meal_Type',
                          title='Demand by Meal Type', text_auto=True)
            st.plotly_chart(fig2, use_container_width=True)

   # Row 2 Charts
    col_chart3, col_chart4 = st.columns(2)
    with col_chart3:
        if not filtered_food.empty:
            city_counts = filtered_food['Location'].value_counts().reset_index().head(7)
            city_counts.columns = ['City', 'Listings']
            fig3 = px.bar(city_counts, x='City', y='Listings', title='Top 7 Cities by Food Listings', color='Listings', color_continuous_scale='Viridis')
            st.plotly_chart(fig3, use_container_width=True)
        
    with col_chart4:
        filtered_claims = df_claims[df_claims['Food_ID'].isin(filtered_food['Food_ID'])]
        
        if not filtered_claims.empty:
            claim_status = filtered_claims['Status'].value_counts().reset_index()
            claim_status.columns = ['Status', 'Count']
            fig4 = px.pie(claim_status, names='Status', values='Count', title='Overall Claim Status Distribution')
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No claims data available for this filter.")


# TAB 2: DATA EXPLORER

with tab2:
    st.markdown("###  Filtered Food Listings")
    st.dataframe(filtered_food[['Food_ID', 'Food_Name', 'Quantity', 'Food_Type', 'Meal_Type', 'Expiry_Date', 'Location']], use_container_width=True)
    
    st.markdown("###  Provider Contact Directory")
    if not filtered_food.empty:
        contact_df = pd.merge(filtered_food[['Provider_ID']], df_providers, on='Provider_ID', how='left').drop_duplicates(subset=['Provider_ID'])
        st.dataframe(contact_df[['Name', 'Type', 'City', 'Contact']], use_container_width=True)


# TAB 3: MANAGE DATA (FULL CRUD OPERATIONS)

with tab3:
    st.markdown("###  Database Management Interface (CRUD)")
    
    # 3 Columns for Create, Update, Delete
    col_crud1, col_crud2, col_crud3 = st.columns(3)
    
    current_ids = df_food['Food_ID'].tolist() if not df_food.empty else []
    
# --- 1. CREATE (Insert New Record) ---
    with col_crud1:
        st.subheader(" Add Listing (CREATE)")
        
        # --- NAYA PRO ID LOGIC YAHAN HAI ---
        if not df_food.empty:
            max_current_id = int(df_food['Food_ID'].max())
            next_valid_id = max_current_id + 1
        else:
            next_valid_id = 10000 
        
        with st.form("add_record_form"):
            new_id = st.number_input("Food ID", min_value=next_valid_id, value=next_valid_id, step=1)
            
            new_name = st.text_input("Food Name (e.g., Dal)")
            new_qty = st.number_input("Quantity", min_value=1, step=1)
            
            provider_list = df_providers['Provider_ID'].tolist() if not df_providers.empty else [1]
            new_prov_id = st.selectbox("Provider ID", provider_list)
            
            new_loc = st.text_input("Location (City)")
            new_meal = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])
            new_food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
            
            if st.form_submit_button("Add Record", use_container_width=True):
                try:
                    with engine.connect() as conn:
                        query = text(f"""
                            INSERT INTO food_listings (Food_ID, Food_Name, Quantity, Provider_ID, Location, Meal_Type, Food_Type) 
                            VALUES ({new_id}, '{new_name}', {new_qty}, {new_prov_id}, '{new_loc}', '{new_meal}', '{new_food_type}')
                        """)
                        conn.execute(query)
                        conn.commit()
                    
                    st.cache_data.clear()
                    st.success(f"Record {new_id} added successfully! ")
                    time.sleep(1.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding: {e}")

    # --- 2. UPDATE (Modify Existing Record) ---
    with col_crud2:
        st.subheader(" Update Listing (UPDATE)")
        
        update_id = st.selectbox("Select ID to Update", current_ids, key="update_id")
        
        if update_id:
            current_row = df_food[df_food['Food_ID'] == update_id].iloc[0]
            
            with st.form("update_record_form"):
                st.info(f"Updating all details for Food ID: {update_id}")
                
                upd_name = st.text_input("Food Name", value=current_row['Food_Name'])
                upd_qty = st.number_input("Quantity", min_value=0, value=int(current_row['Quantity']), step=1)
                
                provider_list = df_providers['Provider_ID'].tolist() if not df_providers.empty else [1]
                prov_index = provider_list.index(current_row['Provider_ID']) if current_row['Provider_ID'] in provider_list else 0
                upd_prov_id = st.selectbox("Provider ID", provider_list, index=prov_index)
                
                upd_loc = st.text_input("Location (City)", value=current_row['Location'])
                
                meal_list = ["Breakfast", "Lunch", "Dinner", "Snacks"]
                meal_index = meal_list.index(current_row['Meal_Type']) if current_row['Meal_Type'] in meal_list else 0
                upd_meal = st.selectbox("Meal Type", meal_list, index=meal_index)
                
                food_list = ["Vegetarian", "Non-Vegetarian", "Vegan"]
                food_index = food_list.index(current_row['Food_Type']) if current_row['Food_Type'] in food_list else 0
                upd_food_type = st.selectbox("Food Type", food_list, index=food_index)
                
                if st.form_submit_button("Update All Fields", use_container_width=True):
                    try:
                        with engine.connect() as conn:
                            query = text(f"""
                                UPDATE food_listings 
                                SET Food_Name = '{upd_name}', 
                                    Quantity = {upd_qty}, 
                                    Provider_ID = {upd_prov_id}, 
                                    Location = '{upd_loc}', 
                                    Meal_Type = '{upd_meal}', 
                                    Food_Type = '{upd_food_type}' 
                                WHERE Food_ID = {update_id}
                            """)
                            conn.execute(query)
                            conn.commit()
                        
                        st.cache_data.clear()
                        st.success(f"Record {update_id} updated successfully! ")
                        time.sleep(1.5) 
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating: {e}")

    # --- 3. DELETE (Remove Record) ---
    with col_crud3:
        st.subheader(" Delete Listing (DELETE)")
        st.warning("Warning: Permanent action.")
        
        delete_id = st.selectbox("Select ID to Delete", current_ids, key="delete_id")
        
        if st.button("Delete Record", type="primary", use_container_width=True):
            try:
                with engine.connect() as conn:
                    query = text(f"DELETE FROM food_listings WHERE Food_ID = {delete_id}")
                    conn.execute(query)
                    conn.commit()
                
                st.cache_data.clear()
                st.success(f"Record {delete_id} deleted successfully! 🗑️")
                time.sleep(1.5)
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting: {e}")