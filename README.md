# Analytics Dashboard Portfolio

A comprehensive analytics dashboard showcasing advanced data analysis capabilities, featuring A/B testing sample size calculators and statistical analysis tools built with Streamlit.

## Key Features

### Analytics Modules
- **LTV Analysis**: Customer lifetime value projections and segmentation
- **Engagement Metrics**: User engagement tracking and behavioral analysis
- **Acquisition Analytics**: User acquisition funnel optimization
- **Monetization Insights**: Revenue analysis and optimization strategies

### A/B Testing Calculators
- **Dual Calculator Interface**: Side-by-side comparison of testing scenarios
- **Standard A/B Testing**: Control vs treatment sample size calculations
- **Multi-Variant Testing**: Advanced testing with Bonferroni correction
- **Statistical Foundation**: Powered by `statsmodels` library
- **Transparent Calculations**: View exact Python code for all computations

## Technical Implementation

- **Framework**: Streamlit
- **Statistics**: statsmodels, scipy, numpy
- **Data Processing**: pandas
- **Python**: 3.8+

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

4. **Access the dashboard** at `http://localhost:8501`

## Statistical Capabilities

### Testing Methods
- **Proportion Testing**: Conversion rates, completion rates, and binary outcomes
- **Continuous Metrics**: Revenue, engagement time, and numerical variables
- **Multiple Comparisons**: Bonferroni correction for multi-variant experiments
- **Power Analysis**: Sample size and statistical power calculations

### Implementation Details
- `statsmodels.stats.power.NormalIndPower` for proportion tests
- `statsmodels.stats.power.TTestIndPower` for continuous variables
- Proper alpha adjustment: `α_adjusted = α / number_of_treatments`
- Support for unequal group allocation ratios

## Dashboard Structure

```
analytics-dashboard-portfolio/
├── streamlit_app.py              # Main application
├── dashboard/                    # Core modules
│   ├── tabs/                    # Feature modules
│   │   ├── abtest/             # A/B testing tools
│   │   ├── ltv/                # Lifetime value analysis
│   │   ├── engagement/         # User engagement metrics
│   │   ├── acquisition/        # User acquisition tracking
│   │   └── monetization/       # Revenue optimization
│   ├── components/             # UI components
│   ├── config/                 # Configuration
│   └── utils/                  # Helper functions
└── requirements.txt            # Dependencies
```

## Professional Applications

- **Analytics Teams**: Comprehensive performance dashboards
- **Data Scientists**: Statistical experimentation toolkit
- **Product Teams**: Data-driven decision making
- **Growth Teams**: Acquisition and retention optimization

## Portfolio Highlights

- **Clean Architecture**: Modular, maintainable code structure
- **Statistical Rigor**: Proper implementation of testing methodologies
- **Professional UI**: Intuitive interface with synchronized layouts
- **Transparent Analysis**: Viewable calculation code for verification

## Contact

For inquiries: where.ai.meets.roi@gmail.com

---

**Professional Analytics Dashboard Portfolio**  
*Demonstrating expertise in statistical analysis, data visualization, and dashboard development*

## 🎯 Professional Applications

- **Analytics Teams**: Comprehensive performance dashboards
- **Data Scientists**: Statistical experimentation toolkit
- **Product Teams**: Data-driven decision making
- **Growth Teams**: Acquisition and retention optimization

## � Portfolio Highlights

- **Clean Architecture**: Modular, maintainable code structure
- **Statistical Rigor**: Proper implementation of testing methodologies
- **Professional UI**: Intuitive interface with synchronized layouts
- **Transparent Analysis**: Viewable calculation code for verification

## 📧 Contact

For inquiries: where.ai.meets.roi@gmail.com

---

**Professional Analytics Dashboard Portfolio**  
*Demonstrating expertise in statistical analysis, data visualization, and dashboard development*
