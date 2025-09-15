import streamlit as st
from google.cloud import bigquery
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import numpy as np
import google.generativeai as genai

# Page configuration
st.set_page_config(
    page_title="Game Analytics Dashboard",
    page_icon="🎮",
    layout="wide"
)

# Data Analysis Helper Functions
class DataAnalyzer:
    @staticmethod
    def analyze_timeseries(data, date_col, value_col):
        """Analyze time series data for trends, patterns, and insights"""
        if data.empty:
            return {}
        
        # Sort by date
        data_sorted = data.sort_values(date_col)
        
        # Basic statistics
        total_value = data_sorted[value_col].sum()
        avg_daily = data_sorted[value_col].mean()
        median_daily = data_sorted[value_col].median()
        std_daily = data_sorted[value_col].std()
        
        # Growth analysis
        first_week = data_sorted.head(7)[value_col].sum()
        last_week = data_sorted.tail(7)[value_col].sum()
        growth_rate = ((last_week - first_week) / first_week * 100) if first_week > 0 else 0
        
        # Peak analysis
        max_day = data_sorted.loc[data_sorted[value_col].idxmax()]
        min_day = data_sorted.loc[data_sorted[value_col].idxmin()]
        
        # Trend detection (simple linear regression)
        x = np.arange(len(data_sorted))
        y = data_sorted[value_col].values
        if len(x) > 1:
            slope = np.polyfit(x, y, 1)[0]
            trend = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
        else:
            trend = "insufficient data"
        
        return {
            "total": int(total_value),
            "avg_daily": round(avg_daily, 1),
            "median_daily": round(median_daily, 1),
            "volatility": round(std_daily, 1),
            "growth_rate": round(growth_rate, 1),
            "peak_value": int(max_day[value_col]),
            "peak_date": str(max_day[date_col]),
            "lowest_value": int(min_day[value_col]),
            "lowest_date": str(min_day[date_col]),
            "trend": trend,
            "data_points": len(data_sorted)
        }
    
    @staticmethod
    def analyze_distribution(data, category_col, value_col):
        """Analyze categorical distribution"""
        if data.empty:
            return {}
            
        distribution = data.groupby(category_col)[value_col].sum().sort_values(ascending=False)
        total = distribution.sum()
        
        # Calculate percentages and insights
        top_category = distribution.index[0]
        top_percentage = (distribution.iloc[0] / total * 100)
        
        # Diversity analysis
        num_categories = len(distribution)
        entropy = -sum((p/total) * np.log2(p/total) for p in distribution if p > 0)
        max_entropy = np.log2(num_categories) if num_categories > 1 else 1
        diversity_score = entropy / max_entropy if max_entropy > 0 else 0
        
        return {
            "total": int(total),
            "num_categories": num_categories,
            "top_category": top_category,
            "top_percentage": round(top_percentage, 1),
            "top_value": int(distribution.iloc[0]),
            "diversity_score": round(diversity_score, 2),
            "distribution": {cat: int(val) for cat, val in distribution.head(5).items()}
        }
    
    @staticmethod
    def analyze_weekly_patterns(data, date_col, value_col):
        """Analyze weekly patterns and seasonality"""
        if data.empty:
            return {}
            
        data = data.copy()
        data['weekday'] = pd.to_datetime(data[date_col]).dt.day_name()
        
        weekly_avg = data.groupby('weekday')[value_col].mean()
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly_avg = weekly_avg.reindex([day for day in weekday_order if day in weekly_avg.index])
        
        best_day = weekly_avg.idxmax()
        worst_day = weekly_avg.idxmin()
        weekend_avg = weekly_avg[['Saturday', 'Sunday']].mean() if 'Saturday' in weekly_avg and 'Sunday' in weekly_avg else 0
        weekday_avg = weekly_avg[['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']].mean()
        
        return {
            "best_day": best_day,
            "best_day_avg": round(weekly_avg[best_day], 1),
            "worst_day": worst_day,
            "worst_day_avg": round(weekly_avg[worst_day], 1),
            "weekend_avg": round(weekend_avg, 1),
            "weekday_avg": round(weekday_avg, 1),
            "weekend_vs_weekday": round(((weekend_avg - weekday_avg) / weekday_avg * 100), 1) if weekday_avg > 0 else 0,
            "pattern": dict(weekly_avg.round(1))
        }

# AI Integration for Dashboard Explanations using Google Gemini
class DashboardExplainer:
    def __init__(self):
        self.ai_enabled = self._setup_gemini()

    def _setup_gemini(self):
        """Setup Google Gemini API"""
        try:
            api_key = None
            if hasattr(st, 'secrets') and 'gemini_api_key' in st.secrets:
                api_key = st.secrets["gemini_api_key"]
            elif 'GEMINI_API_KEY' in os.environ:
                api_key = os.environ['GEMINI_API_KEY']
            
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')  # Updated model name
                # Test the API key with a simple request
                test_response = self.model.generate_content("Hello")
                return True
            else:
                return False
        except Exception as e:
            print(f"Gemini setup error: {e}")  # Debug print
            return False
    
    def explain_chart(self, chart_type, analysis_data, description):
        """Generate AI explanation for chart data"""
        if not self.ai_enabled:
            return None
        
        try:
            prompt = f"""
            Analyze this {chart_type} chart data and provide insights:
            
            Chart Description: {description}
            Data Analysis: {analysis_data}
            
            Provide 2-3 key insights in a conversational tone, focusing on actionable business implications.
            Keep it concise and relevant for game analytics.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception:
            return None

# Initialize explainer
explainer = DashboardExplainer()
    

# Initialize chatbot

# Create API client with cloud deployment support
@st.cache_resource
def get_bigquery_client():
    # For cloud deployment, use demo mode if no credentials
    try:
        return bigquery.Client(project="tactile-471816")
    except Exception:
        return None

@st.cache_data
def get_bigquery_data(query):
    client = get_bigquery_client()
    if client is None:
        st.error("BigQuery client not available. Please check your credentials.")
        return pd.DataFrame()
    
    query_job = client.query(query)
    return query_job.to_dataframe()

# Check if running with BigQuery
DEMO_MODE = get_bigquery_client() is None

# Main title with mode indicator
col1, col2 = st.columns([3, 1])
with col1:
    st.title('🎮 Game Analytics Dashboard')
with col2:
    if explainer.ai_enabled:
        st.success("🤖 AI Insights Enabled")
    else:
        st.error("⚠️ Gemini API Key Required")

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📈 Acquisition", "🎯 Engagement", "💰 Monetisation", "🧪 A/B Test", "📊 LTV", "💬 AI Assistant"])

with tab1:
    st.header("Player Distribution by Launch Phase")
    
    # SQL Query for Player Distribution
    PLAYER_DISTRIBUTION_QUERY = """
    SELECT
      case when install_date is null then null ELSE DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', install_date)) end as install_date,
      CASE 
        WHEN DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', install_date)) < '2022-04-01' THEN 'Soft Launch'
        WHEN DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', install_date)) >= '2022-06-01' THEN 'Official Launch'
        ELSE 'Unknown'
      END as launch_phase,
      case 
        when lower(platform) = 'google_android' then 'android' 
        when lower(platform) = 'apple_ios' then 'ios' 
        else lower(platform) 
      end as platform,
      LEFT(channel_country,2) AS country,
      SPLIT(channel_country, '-')[OFFSET(1)] AS channel_type,
      case when gender is null then "unknown" else gender end as gender,
      CASE 
        WHEN age IS NULL OR age = '' OR age = 'unknown' THEN 'unknown'
        WHEN age = '60+' THEN '60+' 
        WHEN SAFE_CAST(age AS INT64) IS NULL THEN 'unknown'
        WHEN SAFE_CAST(age AS INT64) <=30 THEN '<=30'
        WHEN SAFE_CAST(age AS INT64) BETWEEN 31 AND 40 THEN '31-40'
        WHEN SAFE_CAST(age AS INT64) BETWEEN 41 AND 50 THEN '41-50'
        WHEN SAFE_CAST(age AS INT64) BETWEEN 51 AND 60 THEN '51-60'
        ELSE 'unknown'
      END AS age_group,
      count(DISTINCT user_id) as num_player,
      count(*) as num_device
    FROM `tactile-471816.data_analyst_test_local.users`
    WHERE DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', install_date)) >= '2020-01-01'
      AND DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', install_date)) <= CURRENT_DATE()
    GROUP BY 1, 2, 3, 4, 5, 6, 7
    ORDER BY 1
    """
    
    try:
        # Fetch data
        with st.spinner("Loading player distribution data..."):
            df = get_bigquery_data(PLAYER_DISTRIBUTION_QUERY)
        
        st.success(f"Loaded {len(df)} records")
        
        # Data preprocessing
        df_clean = df.dropna(subset=['install_date'])
        df_clean['install_date'] = pd.to_datetime(df_clean['install_date'], format='%Y-%m-%d', errors='coerce')
        df_clean = df_clean.dropna(subset=['install_date'])
        df_clean = df_clean[(df_clean['install_date'] >= '2020-01-01') & 
                            (df_clean['install_date'] <= pd.Timestamp.now())]
        
        # Display raw data table
        with st.expander("📋 Raw Data Sample", expanded=False):
            st.dataframe(df.head(100))
        
        # CONTAINER 1: Player Acquisition Time Series Analysis
        with st.container():
            st.subheader("📅 Player Acquisition Time Series Analysis")
            
            # Create two columns: plot + AI on left, manual insights on right
            col_plot, col_manual = st.columns([2, 1])
            
            with col_plot:
                timeseries_data = df_clean.groupby('install_date')['num_player'].sum().reset_index()
                
                def assign_region(date):
                    month = date.month
                    if month < 4:
                        return "Canada"
                    elif month >= 6:
                        return "US"
                    else:
                        return "Other"
                
                timeseries_data['region'] = timeseries_data['install_date'].apply(assign_region)
                
                # Plot
                fig1 = px.bar(
                    timeseries_data, 
                    x='install_date', 
                    y='num_player',
                    color='region',
                    color_discrete_map={'Canada': 'red', 'US': 'blue', 'Other': 'gray'},
                    title='Number of Players by Install Date'
                )
                
                fig1.update_layout(
                    xaxis_title='Install Date',
                    yaxis_title='Number of Players',
                    xaxis_tickangle=-45,
                    height=400
                )
                
                st.plotly_chart(fig1, use_container_width=True)
                
                # AI Analysis dropdown under the plot
                analysis = DataAnalyzer.analyze_timeseries(timeseries_data, 'install_date', 'num_player')
                explanation = explainer.explain_chart("timeseries", analysis, "Player acquisition by launch phase showing regional launch strategy")
                if explanation:
                    with st.expander("🤖 AI Analysis", expanded=False):
                        st.info(explanation)
                else:
                    with st.expander("🤖 AI Analysis", expanded=False):
                        st.error("⚠️ Configure Gemini API key in .streamlit/secrets.toml to enable AI insights")
            
            with col_manual:
                st.markdown("**📝 Manual Insights**")
                st.text_area(
                    "Your analysis notes:",
                    placeholder="• Key growth trends observed\n• Regional launch performance\n• Seasonal patterns\n• Marketing effectiveness",
                    height=400,
                    key="timeseries_manual"
                )
        
        # CONTAINER 2: Weekly Patterns Analysis  
        with st.container():
            st.subheader("📊 Weekly Patterns Analysis")
            
            # Create two columns: plot + AI on left, manual insights on right
            col_plot, col_manual = st.columns([2, 1])
            
            df_us = df_clean[df_clean['country'] == 'US'].copy()
            df_us = df_us[df_us['install_date'].dt.month >= 6]  # June onward
            
            if not df_us.empty:
                with col_plot:
                    df_us['day_of_week'] = df_us['install_date'].dt.day_name()
                    df_us['week_start'] = df_us['install_date'] - pd.to_timedelta(df_us['install_date'].dt.weekday, unit='d')
                    df_us['week_label'] = df_us['week_start'].dt.strftime('%Y-%m-%d')
                    
                    # Exclude specific week
                    df_us = df_us[df_us['week_label'] != '2022-06-27']
                    
                    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    df_us['day_of_week'] = pd.Categorical(df_us['day_of_week'], categories=weekday_order, ordered=True)
                    
                    weekly_summary = df_us.groupby(['week_label', 'day_of_week'])['num_player'].sum().reset_index()
                    
                    # Plot
                    fig2 = px.line(
                        weekly_summary,
                        x='day_of_week',
                        y='num_player',
                        color='week_label',
                        markers=True,
                        title='US Player Installs by Day of Week'
                    )
                    
                    fig2.update_layout(
                        xaxis_title='Day of Week',
                        yaxis_title='Number of Players',
                        legend_title='Week Starting',
                        height=400
                    )
                    
                    st.plotly_chart(fig2, use_container_width=True)
                    
                    # AI Analysis dropdown under the plot
                    analysis = DataAnalyzer.analyze_weekly_patterns(df_us, 'install_date', 'num_player')
                    explanation = explainer.explain_chart("weekly_pattern", analysis, "US player acquisition patterns by day of week")
                    if explanation:
                        with st.expander("🤖 AI Analysis", expanded=False):
                            st.info(explanation)
                    else:
                        with st.expander("🤖 AI Analysis", expanded=False):
                            st.error("⚠️ Configure Gemini API key in .streamlit/secrets.toml to enable AI insights")
                
                with col_manual:
                    st.markdown("**📝 Manual Insights**")
                    st.text_area(
                        "Your analysis notes:",
                        placeholder="• Best performing days\n• Marketing timing recommendations\n• User behavior patterns\n• Weekly optimization strategies",
                        height=400,
                        key="weekly_manual"
                    )
            else:
                with col_plot:
                    st.write("No US data available for weekly analysis")
                with col_manual:
                    st.markdown("**📝 Manual Insights**")
                    st.text_area(
                        "Your analysis notes:",
                        placeholder="• Weekly analysis notes will appear here when data is available",
                        height=150,
                        key="weekly_manual_empty"
                    )
        
        # CONTAINER 3: Demographics Distribution Analysis
        with st.container():
            st.subheader("📈 Demographics Distribution Analysis")
            
            # Create two columns: plot + AI on left, manual insights on right
            col_plot, col_manual = st.columns([2, 1])
            
            df_us_dist = df_clean[df_clean['country'] == 'US'].copy()
            
            if not df_us_dist.empty:
                with col_plot:
                    def prepare_data(column, sort_by_value=True, custom_order=None):
                        data = df_us_dist.groupby(column)['num_player'].sum().reset_index()
                        if custom_order:
                            data[column] = pd.Categorical(data[column], categories=custom_order, ordered=True)
                            data = data.sort_values(column)
                        elif sort_by_value:
                            data = data.sort_values('num_player', ascending=False)
                        else:
                            data = data.sort_values(column)
                        return data
                    
                    datasets = {
                        'Platform': prepare_data('platform'),
                        'Gender': prepare_data('gender'),
                        'Channel Type': prepare_data('channel_type'),
                        'Age Group': prepare_data(
                            'age_group', 
                            sort_by_value=False, 
                            custom_order=['<=30', '31-40', '41-50', '51-60', '60+', 'unknown']
                        ),
                    }
                    
                    # Plot
                    fig3 = make_subplots(
                        rows=2, cols=2, 
                        subplot_titles=(
                            'Platform Distribution', 
                            'Gender Distribution', 
                            'Channel Type Distribution', 
                            'Age Group Distribution'
                        ),
                        specs=[[{"type": "bar"}, {"type": "bar"}],
                               [{"type": "bar"}, {"type": "bar"}]]
                    )
                    
                    data_list = list(datasets.values())
                    
                    fig3.add_trace(go.Bar(x=data_list[0]['platform'], y=data_list[0]['num_player']), row=1, col=1)
                    fig3.add_trace(go.Bar(x=data_list[1]['gender'], y=data_list[1]['num_player']), row=1, col=2)
                    fig3.add_trace(go.Bar(x=data_list[2]['channel_type'], y=data_list[2]['num_player']), row=2, col=1)
                    fig3.add_trace(go.Bar(x=data_list[3]['age_group'], y=data_list[3]['num_player']), row=2, col=2)
                    
                    fig3.update_layout(
                        height=600, 
                        showlegend=False, 
                        title_text="US Player Distribution Analysis"
                    )
                    
                    st.plotly_chart(fig3, use_container_width=True)
                    
                    # AI Analysis dropdown under the plot
                    platform_analysis = DataAnalyzer.analyze_distribution(df_us_dist, 'platform', 'num_player')
                    platform_explanation = explainer.explain_chart("distribution", platform_analysis, "US player distribution by mobile platform")
                    
                    age_analysis = DataAnalyzer.analyze_distribution(df_us_dist, 'age_group', 'num_player')
                    age_explanation = explainer.explain_chart("distribution", age_analysis, "US player age demographics")
                    
                    if platform_explanation or age_explanation:
                        with st.expander("🤖 AI Analysis", expanded=False):
                            if platform_explanation:
                                st.success(f"**Platform:** {platform_explanation}")
                            if age_explanation:
                                st.success(f"**Age Groups:** {age_explanation}")
                    else:
                        with st.expander("🤖 AI Analysis", expanded=False):
                            st.error("⚠️ Configure Gemini API key in .streamlit/secrets.toml to enable AI insights")
                
                with col_manual:
                    st.markdown("**📝 Manual Insights**")
                    st.text_area(
                        "Your analysis notes:",
                        placeholder="• Primary audience segments\n• Platform preferences\n• Age group analysis\n• Channel performance\n• Targeting recommendations",
                        height=600,
                        key="demographics_manual"
                    )
            else:
                with col_plot:
                    st.write("No distribution data available")
                with col_manual:
                    st.markdown("**📝 Manual Insights**")
                    st.text_area(
                        "Your analysis notes:",
                        placeholder="• Demographics analysis notes will appear here when data is available",
                        height=200,
                        key="demographics_manual_empty"
                    )
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

with tab2:
    st.header("🎯 Engagement Analytics")
    
    # CONTAINER 1: Daily Active Users Analysis
    with st.container():
        st.subheader("📊 Daily Active Users Analysis")
        st.info("DAU metrics and trends will be displayed here")
        
        # Placeholder for plot
        st.write("📈 *DAU trend chart will be added here*")
        
        # AI Insights and Manual Insights
        col_ai, col_manual = st.columns([1, 1])
        
        with col_ai:
            st.markdown("**🤖 AI Analysis**")
            st.write("*AI insights for DAU trends will appear here*")
        
        with col_manual:
            st.markdown("**📝 Manual Insights**")
            st.text_area(
                "Your DAU analysis notes:",
                placeholder="• DAU growth trends\n• Peak usage periods\n• User engagement drivers\n• Seasonal patterns",
                height=120,
                key="dau_manual"
            )
    
    # CONTAINER 2: Retention Analysis  
    with st.container():
        st.subheader("🔄 Retention Cohort Analysis")
        st.info("Retention cohorts and lifecycle analysis will be displayed here")
        
        # Placeholder for plot
        st.write("📈 *Retention cohort chart will be added here*")
        
        # AI Insights and Manual Insights
        col_ai, col_manual = st.columns([1, 1])
        
        with col_ai:
            st.markdown("**🤖 AI Analysis**")
            st.write("*AI insights for retention patterns will appear here*")
        
        with col_manual:
            st.markdown("**📝 Manual Insights**")
            st.text_area(
                "Your retention analysis notes:",
                placeholder="• Cohort performance\n• Churn indicators\n• Retention drivers\n• Lifecycle optimization",
                height=120,
                key="retention_manual"
            )

with tab3:
    st.header("💰 Monetisation Analytics")
    
    # CONTAINER 1: Revenue Analysis
    with st.container():
        st.subheader("💰 Revenue Trends Analysis")
        st.info("Revenue metrics and ARPU analysis will be displayed here")
        
        # Placeholder for plot
        st.write("📊 *Revenue trend chart will be added here*")
        
        # AI Insights and Manual Insights
        col_ai, col_manual = st.columns([1, 1])
        
        with col_ai:
            st.markdown("**🤖 AI Analysis**")
            st.write("*AI insights for revenue trends will appear here*")
        
        with col_manual:
            st.markdown("**📝 Manual Insights**")
            st.text_area(
                "Your revenue analysis notes:",
                placeholder="• Revenue trends and growth\n• ARPU/ARPPU insights\n• Top revenue drivers\n• Seasonal patterns",
                height=120,
                key="revenue_manual"
            )
    
    # CONTAINER 2: Purchase Behavior
    with st.container():
        st.subheader("🛒 Purchase Behavior Analysis")
        st.info("Purchase patterns and conversion funnels will be displayed here")
        
        # Placeholder for plot
        st.write("📊 *Purchase behavior chart will be added here*")
        
        # AI Insights and Manual Insights
        col_ai, col_manual = st.columns([1, 1])
        
        with col_ai:
            st.markdown("**🤖 AI Analysis**")
            st.write("*AI insights for purchase behavior will appear here*")
        
        with col_manual:
            st.markdown("**📝 Manual Insights**")
            st.text_area(
                "Your purchase analysis notes:",
                placeholder="• Purchase frequency\n• Popular items/features\n• Conversion rates\n• Pricing optimization",
                height=120,
                key="purchase_manual"
            )

with tab4:
    st.header("🧪 A/B Test Analytics")
    
    # CONTAINER 1: Test Results Analysis
    with st.container():
        st.subheader("🧪 Test Performance Comparison")
        st.info("A/B test results and statistical analysis will be displayed here")
        
        # Placeholder for plot
        st.write("📊 *A/B test results chart will be added here*")
        
        # AI Insights and Manual Insights
        col_ai, col_manual = st.columns([1, 1])
        
        with col_ai:
            st.markdown("**🤖 AI Analysis**")
            st.write("*AI insights for test results will appear here*")
        
        with col_manual:
            st.markdown("**📝 Manual Insights**")
            st.text_area(
                "Your A/B test analysis notes:",
                placeholder="• Test winners and losers\n• Statistical significance\n• Impact on key metrics\n• Confidence levels",
                height=120,
                key="abtest_manual"
            )
    
    # CONTAINER 2: Segment Performance
    with st.container():
        st.subheader("📊 Segment Performance Analysis")
        st.info("Segment-specific test results will be displayed here")
        
        # Placeholder for plot
        st.write("📊 *Segment performance chart will be added here*")
        
        # AI Insights and Manual Insights
        col_ai, col_manual = st.columns([1, 1])
        
        with col_ai:
            st.markdown("**🤖 AI Analysis**")
            st.write("*AI insights for segment performance will appear here*")
        
        with col_manual:
            st.markdown("**📝 Manual Insights**")
            st.text_area(
                "Your segment analysis notes:",
                placeholder="• Segment-specific results\n• Demographic variations\n• Behavior differences\n• Implementation decisions",
                height=120,
                key="segment_manual"
            )

with tab5:
    st.header("📊 Lifetime Value (LTV)")
    
    # CONTAINER 1: LTV Cohort Analysis
    with st.container():
        st.subheader("📊 LTV Curves by Cohort")
        st.info("LTV analysis and predictive models will be displayed here")
        
        # Placeholder for plot
        st.write("📊 *LTV cohort chart will be added here*")
        
        # AI Insights and Manual Insights
        col_ai, col_manual = st.columns([1, 1])
        
        with col_ai:
            st.markdown("**🤖 AI Analysis**")
            st.write("*AI insights for LTV trends will appear here*")
        
        with col_manual:
            st.markdown("**📝 Manual Insights**")
            st.text_area(
                "Your LTV analysis notes:",
                placeholder="• Average LTV by cohort\n• LTV growth trends\n• High-value segments\n• Predictive insights",
                height=120,
                key="ltv_manual"
            )
    
    # CONTAINER 2: ROI Analysis
    with st.container():
        st.subheader("💸 ROI & Profitability Analysis")
        st.info("CAC vs LTV and profitability metrics will be displayed here")
        
        # Placeholder for plot
        st.write("📊 *ROI analysis chart will be added here*")
        
        # AI Insights and Manual Insights
        col_ai, col_manual = st.columns([1, 1])
        
        with col_ai:
            st.markdown("**🤖 AI Analysis**")
            st.write("*AI insights for ROI analysis will appear here*")
        
        with col_manual:
            st.markdown("**📝 Manual Insights**")
            st.text_area(
                "Your ROI analysis notes:",
                placeholder="• CAC vs LTV ratios\n• Profitability by channel\n• Payback periods\n• Optimization strategies",
                height=120,
                key="roi_manual"
            )

with tab6:
    st.header("💬 Data Analytics Assistant")
    st.write("Ask questions about your game metrics, data analysis, or get insights about player behavior!")
    
    # Initialize chat history
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hi! I'm your data analytics assistant. I can help you understand your game metrics like retention, revenue, acquisition, and engagement. What would you like to know?"}
        ]
    
    # Display chat messages
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about your data metrics..."):
        # Add user message to chat history
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Prepare context data from the current session
        context_data = "Dashboard showing player acquisition, weekly patterns, demographics distribution"
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your question..."):
                if explainer.ai_enabled:
                    try:
                        ai_prompt = f"""
                        You are a game analytics expert assistant. Answer this question about game data analytics:
                        
                        User Question: {prompt}
                        Context: {context_data}
                        
                        Provide helpful, actionable advice focused on game metrics, player behavior, and business insights.
                        Keep your response concise and practical.
                        """
                        response = explainer.model.generate_content(ai_prompt).text
                    except Exception:
                        response = "I'm having trouble accessing AI insights right now. However, I can still help with general analytics questions. Could you be more specific about what metrics or data you'd like to analyze?"
                else:
                    # Provide basic responses for common questions
                    prompt_lower = prompt.lower()
                    if any(word in prompt_lower for word in ['retention', 'keep', 'return']):
                        response = "To improve retention, focus on: 1) Onboarding optimization - ensure new players understand core mechanics quickly, 2) Daily engagement features like rewards/streaks, 3) Social features to build community, 4) Regular content updates, and 5) Analyzing churn points to fix friction areas."
                    elif any(word in prompt_lower for word in ['revenue', 'monetization', 'money', 'purchase']):
                        response = "For revenue optimization: 1) Analyze your conversion funnel to find drop-off points, 2) A/B test different price points and offers, 3) Implement time-limited offers, 4) Focus on high-LTV user segments, 5) Optimize your in-app purchase flow for minimal friction."
                    elif any(word in prompt_lower for word in ['acquisition', 'users', 'install', 'growth']):
                        response = "User acquisition tips: 1) Analyze your best-performing channels and double down, 2) Optimize your app store presence (ASO), 3) Track cohort performance by source, 4) Test different creative assets, 5) Focus on channels that bring high-LTV users, not just volume."
                    elif any(word in prompt_lower for word in ['metrics', 'kpi', 'track', 'measure']):
                        response = "Key game metrics to track: 1) DAU/MAU for engagement, 2) Retention rates (D1, D7, D30), 3) LTV and ARPU, 4) Conversion rates, 5) Session length and frequency, 6) Churn rate and reasons, 7) Viral coefficient, 8) Cost per acquisition (CPA)."
                    else:
                        response = "I'd be happy to help with your game analytics question! I can provide insights on player retention, revenue optimization, user acquisition, key metrics to track, A/B testing, and more. Could you be more specific about what aspect of your game data you'd like to analyze?"
            
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
    
    # Quick action buttons for common questions
    st.markdown("**💡 Quick Questions:**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📈 How to improve retention?"):
            question = "How can I improve player retention in my game?"
            st.session_state.chat_messages.append({"role": "user", "content": question})
            response = "To improve retention, focus on: 1) Onboarding optimization - ensure new players understand core mechanics quickly, 2) Daily engagement features like rewards/streaks, 3) Social features to build community, 4) Regular content updates, and 5) Analyzing churn points to fix friction areas."
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("💰 Revenue optimization?"):
            question = "What are the best strategies to optimize game revenue?"
            st.session_state.chat_messages.append({"role": "user", "content": question})
            response = "For revenue optimization: 1) Analyze your conversion funnel to find drop-off points, 2) A/B test different price points and offers, 3) Implement time-limited offers, 4) Focus on high-LTV user segments, 5) Optimize your in-app purchase flow for minimal friction."
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col3:
        if st.button("📊 Key metrics to track?"):
            question = "What are the most important metrics I should track for my game?"
            st.session_state.chat_messages.append({"role": "user", "content": question})
            response = "Key game metrics to track: 1) DAU/MAU for engagement, 2) Retention rates (D1, D7, D30), 3) LTV and ARPU, 4) Conversion rates, 5) Session length and frequency, 6) Churn rate and reasons, 7) Viral coefficient, 8) Cost per acquisition (CPA)."
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col4:
        if st.button("🎯 User acquisition tips?"):
            question = "How can I improve my user acquisition strategy?"
            st.session_state.chat_messages.append({"role": "user", "content": question})
            response = "User acquisition tips: 1) Analyze your best-performing channels and double down, 2) Optimize your app store presence (ASO), 3) Track cohort performance by source, 4) Test different creative assets, 5) Focus on channels that bring high-LTV users, not just volume."
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    # Clear chat option
    if st.button("🗑️ Clear Chat", type="secondary"):
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hi! I'm your data analytics assistant. I can help you understand your game metrics like retention, revenue, acquisition, and engagement. What would you like to know?"}
        ]
        st.rerun()
