# Game Analytics Showcase 🎮📊

A comprehensive analytics dashboard for game data analysis, featuring advanced A/B testing sample size calculators and statistical analysis tools.

## 🌟 Features

### Analytics Dashboards
- **LTV Analysis**: Customer lifetime value projections and segmentation
- **Engagement Metrics**: User engagement tracking and analysis
- **Acquisition Analytics**: User acquisition funnel and performance metrics
- **Monetization Insights**: Revenue analysis and monetization optimization

### A/B Testing Tools
- **Dual Calculator Layout**: Side-by-side comparison of testing scenarios
- **1 Control vs 1 Treatment**: Standard A/B test sample size calculation
- **1 Control vs Multiple Treatments**: Advanced multi-variant testing with Bonferroni correction
- **Statistical Rigor**: Proper implementation using `statsmodels` library
- **Interactive Python Code**: Expandable sections showing exact calculations

## 🔧 Technical Stack

- **Frontend**: Streamlit
- **Statistics**: statsmodels, scipy, numpy
- **Data Processing**: pandas
- **Python Version**: 3.8+

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/lilyle-2211/game_analytics_showcase.git
   cd game_analytics_showcase
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Open your browser** to `http://localhost:8501`

## 📊 A/B Testing Calculators

### Features
- **Z-test for Proportions**: Conversion rate and completion rate testing
- **t-test for Continuous Metrics**: Revenue, engagement time, and other continuous variables
- **Bonferroni Correction**: Proper multiple comparison adjustment for multi-variant tests
- **Power Analysis**: Statistical power and sample size calculations
- **Visual Code Display**: See the exact Python code used for calculations

### Statistical Methods
- Uses `statsmodels.stats.power.NormalIndPower` for proportion tests
- Uses `statsmodels.stats.power.TTestIndPower` for continuous metric tests
- Implements proper Bonferroni correction: `α_adjusted = α / number_of_treatments`
- Supports unequal allocation ratios between control and treatment groups

## 📁 Project Structure

```
game_analytics_showcase/
├── streamlit_app.py              # Main application entry point
├── dashboard/                    # Dashboard modules
│   ├── tabs/                    # Individual tab implementations
│   │   ├── abtest/             # A/B testing calculators
│   │   ├── ltv/                # LTV analysis
│   │   ├── engagement/         # Engagement metrics
│   │   ├── acquisition/        # Acquisition analytics
│   │   └── monetization/       # Monetization insights
│   ├── components/             # Reusable UI components
│   ├── config/                 # Configuration settings
│   └── utils/                  # Utility functions
├── requirements.txt            # Python dependencies
└── README.md                  # This file
```

## 🎯 Use Cases

- **Game Analytics Teams**: Comprehensive analytics for game performance
- **Data Scientists**: Statistical testing and experimentation tools
- **Product Managers**: Data-driven decision making dashboard
- **Marketing Teams**: User acquisition and retention analysis

## 📈 Screenshots

The dashboard features:
- Clean, professional interface with color-coded sections
- Synchronized vertical alignment for easy comparison
- Real-time calculations with parameter adjustments
- Expandable Python code sections for transparency

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact

For questions or suggestions, please open an issue or contact: where.ai.meets.roi@gmail.com

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**Built with ❤️ for the analytics community**
Comprehensive Game Analytics Dashboard with A/B Testing Sample Size Calculators - Built with Streamlit, featuring LTV analysis, engagement metrics, acquisition tracking, monetization insights, and advanced statistical testing tools using statsmodels
