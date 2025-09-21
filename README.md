# Game Analytics Dashboard

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/lilyle-2211/analytics-dashboard-portfolio.git
   cd analytics-dashboard-portfolio
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the dashboard**
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Access the dashboard**

   Open your browser to `http://localhost:8501`

## Project Structure

```
analytics-dashboard-portfolio/
├── streamlit_app.py                # Main application
├── dashboard/                      # Core modules
│   ├── tabs/                      # Feature modules
│   │   ├── abtest/               # A/B testing tools
│   │   ├── ltv/                  # Lifetime value analysis
│   │   ├── engagement/           # User engagement metrics
│   │   ├── acquisition/          # User acquisition tracking
│   │   └── monetization/         # Revenue optimization
│   ├── components/               # UI components
│   ├── config/                   # Configuration
│   └── utils/                    # Helper functions
├── sql/                          # SQL queries
│   ├── acquisition_1.sql         # Player distribution analysis
│   ├── engagement_1-4.sql        # Engagement and retention queries
│   ├── monetization_1-2.sql      # Revenue and anomaly detection
│   └── ltv_1-4.sql              # LTV analysis queries
├── ml/                           # Machine learning models
├── data/                         # Sample datasets
└── requirements.txt              # Dependencies
```

## Features

- **Player Acquisition** - User acquisition analysis
- **Engagement Metrics** - Player level and retention analysis
- **Monetization** - Revenue analysis
- **A/B Testing** - Sample size calculators and experiment planning
- **LTV Analysis** - Lifetime value prediction, retention rate and customer segmentation

## Contact

For inquiries: lelisa.dk@gmail.com
