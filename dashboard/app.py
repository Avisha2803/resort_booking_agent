import streamlit as st
import requests
import pandas as pd
import time
import plotly.express as px
from datetime import datetime, timedelta
import json

# Set page configuration
st.set_page_config(
    page_title="🌿 Eco Resort Operations Dashboard",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_URL = "http://localhost:8000"
REFRESH_INTERVAL = 30  # seconds

# Initialize session state
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'order_status_filter' not in st.session_state:
    st.session_state.order_status_filter = ["Pending", "Preparing"]
if 'request_status_filter' not in st.session_state:
    st.session_state.request_status_filter = ["Pending", "In Progress"]
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "orders"
if 'notification' not in st.session_state:
    st.session_state.notification = None

# Custom CSS for eco theme
st.markdown("""
<style>
    /* Eco Theme Colors */
    :root {
        --eco-green: #10b981;
        --eco-green-light: #34d399;
        --eco-green-dark: #065f46;
        --eco-blue: #0ea5e9;
        --eco-yellow: #f59e0b;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
    }
    
    /* Header Styling */
    .eco-header {
        background: linear-gradient(135deg, var(--eco-green), var(--eco-green-dark));
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1.5rem;
    }
    
    /* Card Styling */
    .eco-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(16, 185, 129, 0.1);
        border-left: 4px solid var(--eco-green);
        margin-bottom: 1rem;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--eco-green), var(--eco-green-dark));
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    
    /* Badge Styling */
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .status-pending { background: #fef3c7; color: #92400e; }
    .status-preparing { background: #dbeafe; color: #1e40af; }
    .status-delivered { background: #d1fae5; color: #065f46; }
    .status-cancelled { background: #fee2e2; color: #991b1b; }
    .status-inprogress { background: #e0e7ff; color: #3730a3; }
    .status-completed { background: #dcfce7; color: #166534; }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #f0fdf4;
        padding: 4px;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
    }
    
    /* Notification Styling */
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        animation: slideIn 0.3s ease;
        max-width: 400px;
    }
    
    .notification.success {
        background: #d1fae5;
        color: #065f46;
        border-left: 4px solid var(--eco-green);
    }
    
    .notification.error {
        background: #fee2e2;
        color: #991b1b;
        border-left: 4px solid #ef4444;
    }
    
    .notification.info {
        background: #dbeafe;
        color: #1e40af;
        border-left: 4px solid var(--eco-blue);
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Refresh Animation */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .refreshing {
        animation: spin 1s linear infinite;
    }
</style>
""", unsafe_allow_html=True)

# Title and header with eco theme
st.markdown("""
<div class="eco-header">
    <h1 style="margin:0;">🌿 Eco Resort Operations Dashboard</h1>
    <p style="margin:0.5rem 0 0 0; opacity:0.9;">Monitor orders, service requests, and sustainability metrics</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for controls
with st.sidebar:
    st.markdown("### ⚙️ Dashboard Controls")
    
    # Backend Status
    st.markdown("#### 📊 System Status")
    try:
        health_response = requests.get(f"{API_URL}/health", timeout=2)
        if health_response.status_code == 200:
            status_data = health_response.json()
            st.success(f"✅ **Backend Connected**")
            st.caption(f"Status: {status_data.get('status', 'unknown')}")
            st.caption(f"Database: {status_data.get('database', 'unknown')}")
        else:
            st.warning("⚠️ **Backend Issues**")
    except:
        st.error("❌ **Backend Unavailable**")
        st.info("Start backend with: `uvicorn backend.main:app --reload`")
    
    st.divider()
    
    # Auto-refresh toggle
    col1, col2 = st.columns([3, 1])
    with col1:
        auto_refresh = st.toggle(
            "Auto-refresh",
            value=st.session_state.auto_refresh,
            help="Automatically refresh data every 30 seconds"
        )
    
    with col2:
        refresh_disabled = not st.session_state.auto_refresh
        if st.button("🔄", disabled=refresh_disabled, help="Manual refresh"):
            st.session_state.last_refresh = datetime.now()
            st.rerun()
    
    if auto_refresh:
        st.session_state.auto_refresh = True
        time_since_refresh = (datetime.now() - st.session_state.last_refresh).seconds
        progress = min(time_since_refresh / REFRESH_INTERVAL, 1.0)
        st.progress(progress)
        st.caption(f"Next refresh in {REFRESH_INTERVAL - time_since_refresh}s")
    else:
        st.session_state.auto_refresh = False
    
    st.divider()
    
    # Data filtering section
    st.markdown("#### 🔍 Data Filters")
    
    # Time range filter
    time_range = st.selectbox(
        "Time Range",
        options=["Last 1 hour", "Last 24 hours", "Last 7 days", "Last 30 days", "All time"],
        index=1
    )
    
    # Order status filter
    order_status_options = ["Pending", "Preparing", "Delivered", "Cancelled"]
    selected_order_status = st.multiselect(
        "Order Status",
        options=order_status_options,
        default=st.session_state.order_status_filter,
        help="Filter orders by status"
    )
    st.session_state.order_status_filter = selected_order_status
    
    # Service request status filter
    request_status_options = ["Pending", "In Progress", "Completed", "Cancelled"]
    selected_request_status = st.multiselect(
        "Request Status",
        options=request_status_options,
        default=st.session_state.request_status_filter,
        help="Filter service requests by status"
    )
    st.session_state.request_status_filter = selected_request_status
    
    # Room number filter
    room_filter = st.text_input(
        "Room Number Filter",
        placeholder="e.g., 203, 305",
        help="Filter by specific room number(s), comma separated"
    )
    
    st.divider()
    
    # Export section
    st.markdown("#### 📤 Export Data")
    export_format = st.radio(
        "Export format",
        options=["CSV", "Excel"],
        horizontal=True,
        index=0
    )
    
    if st.button("📊 Download Current View", use_container_width=True):
        st.session_state.last_update = datetime.now()
        st.success("Export ready! (Feature in development)")
    
    st.divider()
    
    # Quick Actions
    st.markdown("#### ⚡ Quick Actions")
    if st.button("✅ Mark All as Completed", use_container_width=True, type="secondary"):
        st.info("This would update all eligible items to completed status")
    
    if st.button("📋 Print Kitchen Tickets", use_container_width=True, type="secondary"):
        st.info("This would generate print jobs for pending orders")

# Data fetching function with error handling
@st.cache_data(ttl=10)  # Cache for 10 seconds
def fetch_data(endpoint, params=None):
    """Fetch data from backend API with error handling"""
    try:
        response = requests.get(f"{API_URL}/{endpoint}", params=params, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch {endpoint}. Status: {response.status_code}")
            return []
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Cannot connect to backend at {API_URL}")
        return []
    except requests.exceptions.Timeout:
        st.error("Request timed out. The server might be slow.")
        return []
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return []

# Function to update order status via API
def update_order_status(order_id, new_status):
    """Update order status by calling backend API"""
    try:
        response = requests.put(
            f"{API_URL}/orders/{order_id}",
            json={"status": new_status},
            timeout=5
        )
        
        if response.status_code == 200:
            return True, "Order status updated successfully!"
        else:
            return False, f"Failed to update order: {response.status_code}"
    except Exception as e:
        return False, f"Error updating order: {str(e)}"

# Function to update service request status via API
def update_request_status(request_id, new_status):
    """Update service request status by calling backend API"""
    try:
        response = requests.put(
            f"{API_URL}/requests/{request_id}",
            json={"status": new_status},
            timeout=5
        )
        
        if response.status_code == 200:
            return True, "Request status updated successfully!"
        else:
            return False, f"Failed to update request: {response.status_code}"
    except Exception as e:
        return False, f"Error updating request: {str(e)}"

# Display notification if exists
if st.session_state.notification:
    notification = st.session_state.notification
    st.markdown(f"""
    <div class="notification {notification['type']}">
        <strong>{notification['icon']} {notification['title']}</strong>
        <p style="margin: 4px 0 0 0; font-size: 0.9rem;">{notification['message']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Clear notification after 3 seconds
    if (datetime.now() - notification['time']).seconds > 3:
        st.session_state.notification = None
        st.rerun()

# Load data with progress indicator
with st.spinner("🌱 Loading eco-resort data..."):
    # Build query parameters
    params = {}
    
    # Apply room filter
    if room_filter:
        room_numbers = [r.strip() for r in room_filter.split(',') if r.strip()]
        if len(room_numbers) == 1:
            params['room_number'] = room_numbers[0]
    
    # Fetch data
    orders = fetch_data("orders", params)
    requests_data = fetch_data("requests", params)
    
    # Update last refresh time
    st.session_state.last_refresh = datetime.now()

# Main dashboard layout with tabs
tab1, tab2, tab3 = st.tabs(["🍽️ Restaurant Orders", "🧹 Service Requests", "📈 Analytics"])

# Tab 1: Restaurant Orders
with tab1:
    if orders:
        df_orders = pd.DataFrame(orders)
        
        if not df_orders.empty:
            # Convert created_at to datetime
            if 'created_at' in df_orders.columns:
                df_orders['created_at'] = pd.to_datetime(df_orders['created_at'])
                
                # Apply time filter
                if time_range == "Last 1 hour":
                    cutoff = datetime.now() - timedelta(hours=1)
                    df_orders = df_orders[df_orders['created_at'] >= cutoff]
                elif time_range == "Last 24 hours":
                    cutoff = datetime.now() - timedelta(hours=24)
                    df_orders = df_orders[df_orders['created_at'] >= cutoff]
                elif time_range == "Last 7 days":
                    cutoff = datetime.now() - timedelta(days=7)
                    df_orders = df_orders[df_orders['created_at'] >= cutoff]
                elif time_range == "Last 30 days":
                    cutoff = datetime.now() - timedelta(days=30)
                    df_orders = df_orders[df_orders['created_at'] >= cutoff]
            
            # Apply status filter
            if 'status' in df_orders.columns and st.session_state.order_status_filter:
                df_orders = df_orders[df_orders['status'].isin(st.session_state.order_status_filter)]
            
            # Format items column
            if 'items' in df_orders.columns:
                df_orders['items_formatted'] = df_orders['items'].apply(
                    lambda x: ", ".join([f"{int(i.get('quantity', 1))}x {i.get('name', 'Unknown')}" 
                                        for i in x]) if isinstance(x, list) else str(x)
                )
            
            # Create sub-tabs for different views
            subtab1, subtab2, subtab3 = st.tabs(["📋 List View", "📊 Charts", "⚡ Manage"])
            
            with subtab1:
                # Display statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    total_orders = len(df_orders)
                    st.metric("Total Orders", total_orders)
                with col2:
                    pending_count = len(df_orders[df_orders['status'] == 'Pending'])
                    st.metric("Pending", pending_count, delta=f"{pending_count} waiting")
                with col3:
                    revenue = df_orders['total_amount'].sum() if 'total_amount' in df_orders.columns else 0
                    st.metric("Total Revenue", f"${revenue:,.2f}")
                with col4:
                    unique_rooms = df_orders['room_number'].nunique() if 'room_number' in df_orders.columns else 0
                    st.metric("Active Rooms", unique_rooms)
                
                # Display dataframe with status badges
                st.markdown("### 📝 Order Details")
                
                # Add status badges column
                df_display = df_orders.copy()
                df_display['status_badge'] = df_display['status'].apply(
                    lambda x: f'<span class="status-badge status-{x.lower().replace(" ", "")}">{x}</span>'
                )
                
                # Select columns to display
                display_cols = []
                column_config = {}
                
                if 'id' in df_display.columns:
                    display_cols.append('id')
                    column_config['id'] = st.column_config.NumberColumn("ID", format="%d")
                
                if 'room_number' in df_display.columns:
                    display_cols.append('room_number')
                    column_config['room_number'] = "Room"
                
                display_cols.append('status_badge')
                column_config['status_badge'] = st.column_config.TextColumn("Status")
                
                if 'total_amount' in df_display.columns:
                    display_cols.append('total_amount')
                    column_config['total_amount'] = st.column_config.NumberColumn("Total", format="$%.2f")
                
                if 'items_formatted' in df_display.columns:
                    display_cols.append('items_formatted')
                    column_config['items_formatted'] = "Items"
                
                if 'created_at' in df_display.columns:
                    display_cols.append('created_at')
                    column_config['created_at'] = "Created At"
                
                # Display the dataframe
                st.dataframe(
                    df_display[display_cols],
                    use_container_width=True,
                    column_config=column_config,
                    hide_index=True
                )
                
                # Export button
                csv = df_display[['id', 'room_number', 'status', 'total_amount', 'items_formatted', 'created_at']].to_csv(index=False)
                st.download_button(
                    label="📥 Download Orders CSV",
                    data=csv,
                    file_name=f"eco_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with subtab2:
                # Create charts
                st.markdown("### 📊 Order Analytics")
                
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    if 'status' in df_orders.columns:
                        status_counts = df_orders['status'].value_counts()
                        if not status_counts.empty:
                            fig1 = px.pie(
                                values=status_counts.values,
                                names=status_counts.index,
                                title="Orders by Status",
                                color_discrete_sequence=['#10b981', '#34d399', '#0ea5e9', '#f59e0b']
                            )
                            st.plotly_chart(fig1, use_container_width=True)
                
                with chart_col2:
                    if 'created_at' in df_orders.columns:
                        df_orders['hour'] = df_orders['created_at'].dt.hour
                        hour_counts = df_orders['hour'].value_counts().sort_index()
                        if not hour_counts.empty:
                            fig2 = px.bar(
                                x=hour_counts.index,
                                y=hour_counts.values,
                                title="Orders by Hour of Day",
                                labels={'x': 'Hour', 'y': 'Count'},
                                color_discrete_sequence=['#10b981']
                            )
                            st.plotly_chart(fig2, use_container_width=True)
                
                # Additional stats
                st.markdown("#### 📈 Performance Metrics")
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                
                with metric_col1:
                    avg_order_value = df_orders['total_amount'].mean() if 'total_amount' in df_orders.columns else 0
                    st.metric("Avg Order Value", f"${avg_order_value:.2f}")
                
                with metric_col2:
                    busiest_hour = hour_counts.idxmax() if not hour_counts.empty else "N/A"
                    st.metric("Busiest Hour", f"{busiest_hour}:00")
                
                with metric_col3:
                    if 'created_at' in df_orders.columns:
                        df_orders['date'] = df_orders['created_at'].dt.date
                        orders_per_day = df_orders['date'].value_counts().mean()
                        st.metric("Avg Orders/Day", f"{orders_per_day:.1f}")
            
            with subtab3:
                # Order management interface
                st.markdown("### ⚡ Manage Orders")
                
                if not df_orders.empty:
                    # Create a form for updating order status
                    with st.form("update_order_form"):
                        st.markdown("#### Update Order Status")
                        
                        # Select order
                        order_options = []
                        for _, row in df_orders.iterrows():
                            order_text = f"#{row['id']} - Room {row['room_number']} - {row['status']}"
                            if 'items_formatted' in row:
                                items_preview = row['items_formatted'][:30] + "..." if len(row['items_formatted']) > 30 else row['items_formatted']
                                order_text += f" ({items_preview})"
                            order_options.append((row['id'], order_text))
                        
                        selected_order = st.selectbox(
                            "Select Order",
                            options=[opt[1] for opt in order_options],
                            key="order_select_manage"
                        )
                        
                        # Get selected order ID
                        selected_order_id = None
                        for order_id, order_text in order_options:
                            if order_text == selected_order:
                                selected_order_id = order_id
                                break
                        
                        # Status selection
                        col1, col2 = st.columns(2)
                        with col1:
                            new_status = st.selectbox(
                                "New Status",
                                options=["Pending", "Preparing", "Delivered", "Cancelled"],
                                index=0,
                                key="order_status_select"
                            )
                        
                        with col2:
                            urgency = st.select_slider(
                                "Urgency Level",
                                options=["Low", "Medium", "High"],
                                value="Medium"
                            )
                        
                        # Notes
                        notes = st.text_area(
                            "Add Notes (Optional)",
                            placeholder="Add any notes about this order update...",
                            help="These notes will be visible to staff"
                        )
                        
                        # Submit button
                        submit_col1, submit_col2 = st.columns([3, 1])
                        with submit_col1:
                            update_order = st.form_submit_button(
                                "🔄 Update Order Status",
                                use_container_width=True,
                                type="primary"
                            )
                        
                        with submit_col2:
                            cancel_order = st.form_submit_button(
                                "❌ Cancel Order",
                                use_container_width=True,
                                type="secondary"
                            )
                        
                        if update_order and selected_order_id:
                            # Call API to update order
                            success, message = update_order_status(selected_order_id, new_status)
                            
                            if success:
                                st.session_state.notification = {
                                    'type': 'success',
                                    'icon': '✅',
                                    'title': 'Success!',
                                    'message': f'Order #{selected_order_id} updated to {new_status}',
                                    'time': datetime.now()
                                }
                                st.session_state.last_refresh = datetime.now()
                                st.rerun()
                            else:
                                st.session_state.notification = {
                                    'type': 'error',
                                    'icon': '❌',
                                    'title': 'Update Failed',
                                    'message': message,
                                    'time': datetime.now()
                                }
                                st.rerun()
                        
                        if cancel_order and selected_order_id:
                            # Call API to cancel order
                            success, message = update_order_status(selected_order_id, "Cancelled")
                            
                            if success:
                                st.session_state.notification = {
                                    'type': 'info',
                                    'icon': 'ℹ️',
                                    'title': 'Order Cancelled',
                                    'message': f'Order #{selected_order_id} has been cancelled',
                                    'time': datetime.now()
                                }
                                st.session_state.last_refresh = datetime.now()
                                st.rerun()
                            else:
                                st.session_state.notification = {
                                    'type': 'error',
                                    'icon': '❌',
                                    'title': 'Cancellation Failed',
                                    'message': message,
                                    'time': datetime.now()
                                }
                                st.rerun()
                    
                    # Batch actions
                    st.markdown("---")
                    st.markdown("#### 🚀 Batch Actions")
                    
                    batch_col1, batch_col2, batch_col3 = st.columns(3)
                    
                    with batch_col1:
                        if st.button("✅ Mark All as Delivered", use_container_width=True):
                            st.info("This would update all pending orders to delivered status")
                    
                    with batch_col2:
                        if st.button("📋 Print Kitchen Tickets", use_container_width=True):
                            st.info("This would generate print jobs for all preparing orders")
                    
                    with batch_col3:
                        if st.button("🔄 Refresh Orders", use_container_width=True):
                            st.session_state.last_refresh = datetime.now()
                            st.rerun()
        else:
            st.info("📭 No orders found with the current filters.")
    else:
        st.info("📭 No orders data available. Check backend connection.")

# Tab 2: Service Requests (similar structure to orders but shorter for brevity)
with tab2:
    if requests_data:
        df_requests = pd.DataFrame(requests_data)
        
        if not df_requests.empty:
            # Similar processing as orders...
            st.markdown("### 🧹 Service Requests Management")
            
            # Quick stats
            col1, col2, col3 = st.columns(3)
            with col1:
                total_requests = len(df_requests)
                st.metric("Total Requests", total_requests)
            with col2:
                pending_req = len(df_requests[df_requests['status'] == 'Pending'])
                st.metric("Pending", pending_req)
            with col3:
                active_rooms = df_requests['room_number'].nunique() if 'room_number' in df_requests.columns else 0
                st.metric("Active Rooms", active_rooms)
            
            # Display and manage requests
            # ... (similar to orders tab but for service requests)
            
            st.info("🛠️ Service request management interface would be similar to orders tab")
    
    else:
        st.info("📭 No service requests data available.")

# Tab 3: Analytics
with tab3:
    st.markdown("### 📈 Resort Performance Analytics")
    
    # Placeholder for analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("🌿 Eco Score", "92%", "3% ↑")
        st.metric("💚 Guest Satisfaction", "94%", "2% ↑")
    
    with col2:
        st.metric("⏱️ Avg Response Time", "8.2 min", "1.3 min ↓")
        st.metric("📊 Occupancy Rate", "78%", "5% ↑")
    
    st.info("📊 Advanced analytics and sustainability metrics would be displayed here")

# Footer
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns([2, 1, 1])

with footer_col1:
    last_update = st.session_state.last_refresh.strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"🕒 Last updated: {last_update}")
    if st.session_state.auto_refresh:
        st.caption(f"🔄 Auto-refresh enabled ({REFRESH_INTERVAL}s interval)")

with footer_col2:
    if st.button("🔄 Force Refresh", use_container_width=True, type="secondary"):
        st.session_state.last_refresh = datetime.now()
        st.rerun()

with footer_col3:
    if st.button("📊 Export All Data", use_container_width=True, type="secondary"):
        st.info("Export feature in development")

# Auto-refresh logic
if st.session_state.auto_refresh:
    time_since_refresh = (datetime.now() - st.session_state.last_refresh).seconds
    if time_since_refresh >= REFRESH_INTERVAL:
        st.session_state.last_refresh = datetime.now()
        st.rerun()

