"""About & Methodology page view."""

from views.shared import (
    _layout,
    _sidebar
)

def page_about() -> str:
    return _layout(
        "About & Methodology",
        "A detailed guide to the Databricks Medallion Lakehouse pipeline, Machine Learning model details, and Recommendation Engine logic.",
        """
        <div class='card-shell mb-4'>
          <h3 class='section-title mt-0' style='border-bottom:none; padding-bottom:0;'>System Architecture & Tech Stack</h3>
          <p>This application operates as a downstream client dashboard connected directly to a production-grade <strong>Databricks SQL Warehouse</strong>. The core data pipeline is designed on top of the <strong>Delta Lake Medallion Architecture</strong>, using the pipeline code defined in the Databricks workspace folder <code>AI_Advisor</code>. The complete pipeline contains 8 sequential stages, from raw ingestion to model recommendation deployment:</p>
          
          <div class='row g-3 mt-1'>
            <div class='col-md-6 col-lg-3'>
              <div class='p-3 border rounded bg-light height-100'>
                <strong style='color:var(--accent);'>Databricks Lakehouse</strong>
                <p class='small text-muted mb-0 mt-1'>Unified Delta Tables storing Bronze, Silver, and Gold stock datasets in the <code>workspace.investment_db</code> schema.</p>
              </div>
            </div>
            <div class='col-md-6 col-lg-3'>
              <div class='p-3 border rounded bg-light height-100'>
                <strong style='color:var(--accent-2);'>MLflow Registry</strong>
                <p class='small text-muted mb-0 mt-1'>Logs model runs, parameters, metrics (R&sup2;, RMSE, MAE), and hosts the production-registered <code>investmentreturnpredictor</code> model.</p>
              </div>
            </div>
            <div class='col-md-6 col-lg-3'>
              <div class='p-3 border rounded bg-light height-100'>
                <strong style='color:var(--accent-3);'>Streamlit App Shell</strong>
                <p class='small text-muted mb-0 mt-1'>Web app powered by <code>databricks-sdk</code> to execute live warehouse queries and query Llama 3.3 conversational chatbot endpoints.</p>
              </div>
            </div>
            <div class='col-md-6 col-lg-3'>
              <div class='p-3 border rounded bg-light height-100'>
                <strong style='color:var(--accent-4);'>Pipeline Scripts</strong>
                <p class='small text-muted mb-0 mt-1'>Calculations based on 8 key notebook files (<code>Setup.py</code>, <code>ingestion.py</code>, <code>cleaning.py</code>, <code>feature_engineering.py</code>, <code>recommendation/investment_advisor.py</code>, etc.).</p>
              </div>
            </div>
          </div>
        </div>

        <div class='card-shell mb-4'>
          <h3 class='section-title mt-0'>The Medallion Data Pipeline</h3>
          <p>Data calculations and integration are processed across three Delta Lake layers inside Databricks:</p>
          <ol class='list-group list-group-numbered border-0 px-0'>
            <li class='list-group-item d-flex justify-content-between align-items-start border-0 px-0'>
              <div class='ms-2 me-auto'>
                <div class='fw-bold' style='color:#7f7f7f;'>Bronze Layer (Raw Ingestion - <code>ingestion.py</code>)</div>
                Downloads daily market data (OHLCV) using the <code>yfinance</code> library for 10 major blue-chip equities from the configured start date. Ticker and Sector attributes are appended, and raw records are written directly to <code>bronze_stock_data</code>.
              </div>
            </li>
            <li class='list-group-item d-flex justify-content-between align-items-start border-0 px-0'>
              <div class='ms-2 me-auto'>
                <div class='fw-bold' style='color:#1f77b4;'>Silver Layer (Data Cleaning - <code>cleaning.py</code>)</div>
                Performs data quality checks: removes duplicate timestamps, filters out invalid negative close prices/volumes, casts values to Spark data types, and logs an <code>ingestion_timestamp</code> metadata flag into <code>silver_stock_data</code>.
              </div>
            </li>
            <li class='list-group-item d-flex justify-content-between align-items-start border-0 px-0'>
              <div class='ms-2 me-auto'>
                <div class='fw-bold' style='color:#2ca02c;'>Gold Layer (Feature Engineering - <code>feature_engineering.py</code>)</div>
                Utilizes PySpark Window functions partitioned by <code>Ticker</code> and ordered by <code>Date</code> to calculate indicators:
                <ul>
                  <li><code>Prev_Close</code>: Closing price of the previous trading day.</li>
                  <li><code>Daily_Return</code>: Annualized percentage daily return, computed as <code>((Close - Prev_Close) / Prev_Close) * 100</code>.</li>
                  <li><code>SMA_7</code> &amp; <code>SMA_30</code>: 7-day and 30-day Simple Moving Averages of the closing price.</li>
                  <li><code>Volatility</code>: 30-day rolling standard deviation of <code>Daily_Return</code>, representing dispersion ratios.</li>
                  <li><code>Future_Return</code>: Target label defined as next-day percentage price change.</li>
                </ul>
                The final datasets are stored in the optimized Delta table <code>gold_stock_features</code>.
              </div>
            </li>
          </ol>
        </div>

        <div class='card-shell mb-4'>
          <h3 class='section-title mt-0'>Machine Learning & Model Evaluation</h3>
          <p>Various regression models were trained in Databricks to predict returns. In the production pipeline, models are logged via MLflow, and the best-performing weekly GBT (Gradient Boosted Trees) Regressor model is registered to serving endpoints. Model performance comparison:</p>
          
          <div class='table-wrap'>
            <table class='table table-striped table-hover mb-0'>
              <thead>
                <tr>
                  <th>Model Type</th>
                  <th>Target Horizon</th>
                  <th>RMSE</th>
                  <th>MAE</th>
                  <th>R&sup2; Score</th>
                  <th>Directional Accuracy</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Random Forest (Baseline)</strong></td>
                  <td>Daily (1-Day) Return</td>
                  <td>2.5919</td>
                  <td>1.6910</td>
                  <td class='text-danger'>-0.0075</td>
                  <td>50.55%</td>
                </tr>
                <tr>
                  <td><strong>GBT Regressor (Enhanced)</strong></td>
                  <td>Daily (1-Day) Return</td>
                  <td>2.7500</td>
                  <td>1.8200</td>
                  <td class='text-danger'>-0.0821</td>
                  <td>50.55%</td>
                </tr>
                <tr class='table-success'>
                  <td><strong>Weekly GBT Regressor (Production)</strong></td>
                  <td>Weekly (5-Day) Return</td>
                  <td><strong>5.5100</strong></td>
                  <td><strong>3.4200</strong></td>
                  <td class='text-success'><strong>+0.0190</strong></td>
                  <td><strong>57.00%</strong></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class='card-shell mb-4'>
          <h3 class='section-title mt-0'>Recommendation Engine Logic</h3>
          <p>The latest recommendations are calculated in <code>investment_advisor.py</code> by querying the registered MLflow production model over the newest gold features, applying the following criteria:</p>
          
          <div class='row g-3'>
            <div class='col-md-4'>
              <div class='p-3 border rounded height-100' style='border-top:4px solid var(--accent-2) !important;'>
                <h5>1. Signal Rules</h5>
                <p class='small text-muted'>Classifies signals based on predicted returns:</p>
                <ul class='small ps-3 mb-0'>
                  <li><strong class='text-success'>BUY:</strong> predicted return &gt; 0.08%</li>
                  <li><strong class='text-warning'>HOLD:</strong> predicted return between -0.03% and 0.08%</li>
                  <li><strong class='text-danger'>AVOID:</strong> predicted return &le; -0.03%</li>
                </ul>
              </div>
            </div>
            <div class='col-md-4'>
              <div class='p-3 border rounded height-100' style='border-top:4px solid var(--accent-3) !important;'>
                <h5>2. Confidence Score</h5>
                <p class='small text-muted'>Calculated by subtracting a volatility penalty from the base predicted return magnitude:</p>
                <div class='p-2 bg-light font-monospace text-center small rounded'>
                  Base = min(|Predicted Return| / 5.0, 1.0)<br/>
                  Penalty = min(Volatility / 3.0, 0.3)<br/>
                  Confidence = max(Base - Penalty, 0.1) &times; 100
                </div>
                <p class='small text-muted mt-2 mb-0'>Expressed from 1 to 10. Higher volatility reduces overall rating score confidence.</p>
              </div>
            </div>
            <div class='col-md-4'>
              <div class='p-3 border rounded height-100' style='border-top:4px solid var(--accent-4) !important;'>
                <h5>3. Risk Category</h5>
                <p class='small text-muted'>Classified based on asset standard deviation limits:</p>
                <ul class='small ps-3 mb-0'>
                  <li><strong>HIGH Risk:</strong> Volatility &gt; 2.0% or predicted return amplitude &gt; 4.0%</li>
                  <li><strong>MEDIUM Risk:</strong> Volatility &gt; 1.0% or predicted return amplitude &gt; 2.0%</li>
                  <li><strong>LOW Risk:</strong> Volatility &le; 1.0% and return amplitude &le; 2.0%</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div class='card-shell mt-3'>
          <h3 class='section-title mt-0'>Pipeline Flow Diagram</h3>
          <div class='empty-state text-center font-monospace small py-3'>
            [Yahoo Finance API Extraction] &rarr; <span class='text-muted'>Delta Bronze Table</span> &rarr; [Data Cleaning & Schema Casting] &rarr; <span class='text-primary'>Delta Silver Table</span><br/>
            &darr;<br/>
            [Rolling Window Aggregations (SMA, Volatility)] &rarr; <span class='text-success'>Delta Gold Table</span> &rarr; [MLflow Registry / GBT model] &rarr; [Recommendation Calculations]<br/>
            &darr;<br/>
            <span class='text-warning'>Delta investment_recommendations Table</span> &rarr; [Databricks SQL Warehouse] &rarr; [Streamlit Dashboard Shell]
          </div>
        </div>
        """,
        _sidebar("About"),
    )
