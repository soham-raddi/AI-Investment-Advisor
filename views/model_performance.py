"""Model Performance evaluation dashboard view."""

import pandas as pd
import plotly.express as px
from views.shared import (
    _layout,
    _sidebar,
    _fig_div,
    _fmt_number,
    page_card_grid,
    page_table
)

def page_model_performance(models: pd.DataFrame | None = None) -> str:
    fig = px.bar(
        models, 
        x='Model', 
        y='R2', 
        color='Model', 
        title='Model R² Score Comparison',
        color_discrete_sequence=px.colors.qualitative.Set2
    ) if models is not None and not models.empty else None
    return _layout(
        "Model Performance",
        "Model comparison and evaluation metrics, styled as a governance dashboard.",
        f"""
        {page_card_grid([
            ("Models", f"{len(models):,}" if models is not None else "0", "Candidate models evaluated", "#1f77b4"),
            ("Best R²", _fmt_number(models['R2'].max(), 3) if models is not None and not models.empty else "N/A", "Highest score", "#2ca02c"),
            ("Lowest RMSE", _fmt_number(models['RMSE'].min(), 3) if models is not None and not models.empty else "N/A", "Best error rate", "#ff7f0e"),
            ("Lowest MAE", _fmt_number(models['MAE'].min(), 3) if models is not None and not models.empty else "N/A", "Best absolute error", "#d62728"),
        ])}
        <div class='two-col'>
          <div class='card-shell'>
            <h3 class='section-title mt-0'>Evaluation Table</h3>
            {page_table(models.assign(RMSE=models['RMSE'].apply(lambda x: _fmt_number(x, 4)), MAE=models['MAE'].apply(lambda x: _fmt_number(x, 4)), R2=models['R2'].apply(lambda x: _fmt_number(x, 4))) if models is not None and not models.empty else models, ['Model', 'RMSE', 'MAE', 'R2']) if models is not None and not models.empty else '<div class="empty-state">No model data available.</div>'}
          </div>
          <div class='card-shell'>
            <h3 class='section-title mt-0'>Model Parameter Glossary</h3>
            <p class='small text-muted'>Understanding the evaluation metrics used to screen and govern the recommendation engine:</p>

            <div class='mb-3'>
              <div class='fw-bold' style='color:var(--accent-2);'>1. R&sup2; (Coefficient of Determination)</div>
              <p class='small text-muted mb-1'><strong>What it means:</strong> Measures the proportion of variance in stock returns that is predictable from the input features (price history, moving averages, volatility).</p>
              <p class='small text-muted mb-1'><strong>What it achieves:</strong> Quantifies how much better the model is than a simple average-rate baseline.</p>
              <div class='small mb-2'>
                <strong>Scale / Interpretation:</strong>
                <table class='table table-sm table-bordered mt-1 mb-0' style='font-size:0.8rem;'>
                  <tr class='table-danger'>
                    <td style='width:35%;'><strong>&le; 0.0</strong></td>
                    <td><strong>Poor / Bad:</strong> Predicts worse than the average baseline (typical for daily market returns due to extreme noise/random walk).</td>
                  </tr>
                  <tr class='table-warning'>
                    <td style='width:35%;'><strong>0.01 to 0.05</strong></td>
                    <td><strong>Acceptable / Good:</strong> Explains 1-5% of variance. In quantitative finance, an R&sup2; of 1-2% is highly valuable and sufficient for establishing a profitable statistical edge.</td>
                  </tr>
                  <tr class='table-success'>
                    <td style='width:35%;'><strong>&gt; 0.10</strong></td>
                    <td><strong>Excellent:</strong> High predictive power (rarely achievable on daily stock price returns without overfitting).</td>
                  </tr>
                </table>
              </div>
            </div>

            <div class='mb-3'>
              <div class='fw-bold' style='color:var(--accent-3);'>2. RMSE (Root Mean Squared Error)</div>
              <p class='small text-muted mb-1'><strong>What it means:</strong> The standard deviation of the prediction residuals. It measures the average magnitude of forecast error, penalizing larger deviations more heavily due to squaring.</p>
              <p class='small text-muted mb-1'><strong>What it achieves:</strong> Pinpoints the model's sensitivity to large forecast failures or outliers.</p>
              <div class='small mb-2'>
                <strong>Scale / Interpretation:</strong>
                <table class='table table-sm table-bordered mt-1 mb-0' style='font-size:0.8rem;'>
                  <tr class='table-success'>
                    <td><strong>&lt; 2.0%</strong></td>
                    <td><strong>Good:</strong> Standard daily deviations are tight (indicates high prediction stability).</td>
                  </tr>
                  <tr class='table-warning'>
                    <td><strong>2.0% to 5.0%</strong></td>
                    <td><strong>Moderate:</strong> Common error range for stock return models due to historical volatility spikes.</td>
                  </tr>
                  <tr class='table-danger'>
                    <td><strong>&gt; 5.0%</strong></td>
                    <td><strong>Bad:</strong> Very large average errors, indicating unstable predictions or heavy outlier impact.</td>
                  </tr>
                </table>
              </div>
            </div>

            <div class='mb-2'>
              <div class='fw-bold' style='color:var(--accent-4);'>3. MAE (Mean Absolute Error)</div>
              <p class='small text-muted mb-1'><strong>What it means:</strong> The average of the absolute differences between predictions and actual values. All individual errors are weighted equally.</p>
              <p class='small text-muted mb-1'><strong>What it achieves:</strong> Represents the expected error deviation on any random day without outlier bias.</p>
              <div class='small'>
                <strong>Scale / Interpretation:</strong>
                <table class='table table-sm table-bordered mt-1 mb-0' style='font-size:0.8rem;'>
                  <tr class='table-success'>
                    <td><strong>&lt; 1.5%</strong></td>
                    <td><strong>Good:</strong> Model forecasts stay close to actual daily returns.</td>
                  </tr>
                  <tr class='table-warning'>
                    <td><strong>1.5% to 3.0%</strong></td>
                    <td><strong>Moderate:</strong> Standard deviation bounds for blue-chip stock movements.</td>
                  </tr>
                  <tr class='table-danger'>
                    <td><strong>&gt; 3.0%</strong></td>
                    <td><strong>Bad:</strong> High average deviation, suggesting poor overall fit.</td>
                  </tr>
                </table>
              </div>
            </div>
          </div>
        </div>
        <div class='card-shell mt-3'>
          <h3 class='section-title mt-0'>R² Comparison</h3>
          {_fig_div(fig, 'model_r2_chart')}
        </div>
        """,
        _sidebar("Model Performance"),
    )
