<h1 style="color:#1E90FF;">🟦 Product Availability & Pricing Normalization Service</h1>
<h3><i>FastAPI • Redis • Async Vendor Aggregation • Circuit Breaker • Caching • Background Prewarming</i></h3>

<p>
  This service aggregates availability and pricing from multiple vendors, normalizes formats, selects the best vendor using business rules, and caches the results for fast performance.  
  It is fully asynchronous, production-oriented, and designed for extensibility.
</p>

<hr/>

<h2>📘 Table of Contents</h2>
<ol>
  <li><a href="#overview">Overview</a></li>
  <li><a href="#architecture">Architecture</a></li>
  <li><a href="#request-flow">High-Level Flow</a></li>
  <li><a href="#normalization-rules">Vendor Normalization Rules</a></li>
  <li><a href="#best-vendor-selection">Best Vendor Selection</a></li>
  <li><a href="#caching">Caching Strategy</a></li>
  <li><a href="#circuit-breaker">Circuit Breaker System</a></li>
  <li><a href="#rate-limiting">Rate Limiting</a></li>
  <li><a href="#background-worker">Background Worker</a></li>
  <li><a href="#api-documentation">API Documentation</a></li>
  <li><a href="#installation">Setup & Installation</a></li>
  <li><a href="#project-structure">Project Structure</a></li>
</ol>

<hr/>

<h1 id="overview" style="color:#1E90FF;">🟦 1. Overview</h1>

<p>This service:</p>

<ul>
  <li>Fetches availability & pricing from <b>VendorA</b>, <b>VendorB</b>, and <b>VendorC</b></li>
  <li>Normalizes vendor-specific data into a unified format</li>
  <li>Selects the best vendor using:
    <ul>
      <li>Price comparison</li>
      <li>Stock evaluation</li>
      <li>Threshold-based hybrid rules</li>
    </ul>
  </li>
  <li>Implements:
    <ul>
      <li>Circuit breaker per vendor</li>
      <li>Retry with exponential backoff</li>
      <li>Redis caching</li>
      <li>Request rate limiting</li>
      <li>Popularity ranking with Redis sorted sets</li>
      <li>Background cache prewarming</li>
    </ul>
  </li>
</ul>

<hr/>

<h1 id="architecture" style="color:#1E90FF;">🟦 2. Architecture</h1>

<p align="center">
  <img src="https://drive.google.com/file/d/14lPSQVdmM86LqluwLzWhMVQCzXAX9Tg_/view?usp=sharing" width="700"/>
</p>

<hr/>

<h1 id="request-flow" style="color:#1E90FF;">🟦 3. High-Level Request Flow</h1>

<p align="center">
  <img src="https://drive.google.com/uc?export=view&id=1XlpoRBJgkizV6UQa85XUZTS6OWToR1A1" width="700"/>
</p>

<hr/>

<h1 id="normalization-rules" style="color:#1E90FF;">🟦 4. Vendor Normalization Rules</h1>

<table>
  <thead>
    <tr>
      <th>Vendor</th>
      <th>Raw Fields</th>
      <th>Normalized Price</th>
      <th>Normalized Stock</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>VendorA</b></td>
      <td>cost, qty, availability</td>
      <td>cost</td>
      <td>qty</td>
    </tr>
    <tr>
      <td><b>VendorB</b></td>
      <td>price_cents, stock</td>
      <td>price_cents / 100</td>
      <td>stock</td>
    </tr>
    <tr>
      <td><b>VendorC</b></td>
      <td>pricing, inventory_level, available</td>
      <td>pricing</td>
      <td>inventory_level or 5 if available == true</td>
    </tr>
  </tbody>
</table>

<hr/>

<h1 id="best-vendor-selection" style="color:#1E90FF;">🟦 5. Best Vendor Selection Logic</h1>

<p align="center">
  <img src="https://drive.google.com/uc?export=view&id=12udWwo__mLbAJuJcUDayPc_HpzgqwpPo" width="700"/>
</p>

<hr/>

<h1 id="caching" style="color:#1E90FF;">🟦 6. Caching Strategy</h1>

<p>SKU popularity tracking:</p>

<pre><code>ZINCRBY stats:sku_requests 1 {sku}</code></pre>

<p>Normalized vendor cache:</p>
<ul>
  <li>Key: <code>product:{sku}</code></li>
  <li>TTL: configurable</li>
  <li>Greatly reduces vendor API calls</li>
</ul>

<hr/>

<h1 id="circuit-breaker" style="color:#1E90FF;">🟦 7. Circuit Breaker System</h1>

<p>The system tracks:</p>
<ul>
  <li>Consecutive failures</li>
  <li>Timeout errors</li>
  <li>Half-open retry windows</li>
</ul>

<p>This prevents hammering unresponsive vendors.</p>

<hr/>

<h1 id="rate-limiting" style="color:#1E90FF;">🟦 8. Rate Limiting</h1>

<pre><code>
INCR ratelimit:{x_api_key}
EXPIRE 60
</code></pre>

<p>If the counter exceeds the threshold → <b>429 Too Many Requests</b>.</p>

<hr/>

<h1 id="background-worker" style="color:#1E90FF;">🟦 9. Background Worker</h1>

<p>Top 10 most popular SKUs:</p>

<pre><code>ZREVRANGE stats:sku_requests 0 9</code></pre>

<p align="center">
  <img src="https://drive.google.com/uc?export=view&id=1e1He8w7DC7aTdRnm4oJ8Sx48B-9ll2uF" width="700"/>
</p>

<hr/>

<h1 id="api-documentation" style="color:#1E90FF;">🟦 10. API Documentation</h1>

<h3>GET <code>/products/{sku}</code></h3>

<p><b>Headers</b></p>
<pre><code>X-API-Key: your_api_key</code></pre>

<p><b>Path Parameter</b></p>
<ul>
  <li><code>sku</code>: 3–20 alphanumeric characters</li>
</ul>

<p><b>Example Response</b>:</p>

<pre><code>{
  "sku": "validsku",
  "status": "IN_STOCK",
  "best_vendor": "VendorA",
  "vendors": [
    {
      "vendor_name": "VendorA",
      "normalized_price": 12.5,
      "normalized_stock": 8
    }
  ]
}
</code></pre>

<p>
  API Docs:  
  <a href="http://localhost:8000/docs">http://localhost:8000/docs</a>
</p>

<hr/>

<h1 id="installation" style="color:#1E90FF;">🟦 11. Setup & Installation</h1>

<h3>1. Clone repository</h3>
<pre><code>git clone &lt;your-repo-url&gt;
cd project-folder
</code></pre>

<h3>2. Install dependencies</h3>
<pre><code>pip install -r requirements.txt
</code></pre>

<h3>3. Start Redis</h3>
<pre><code>redis-server
</code></pre>

<h3>4. Run application</h3>
<pre><code>uvicorn app.main:app --reload
</code></pre>

<h3>5. Open docs</h3>
<p><a href="http://localhost:8000/docs">http://localhost:8000/docs</a></p>

<hr/>

<h1 id="project-structure" style="color:#1E90FF;">🟦 12. Project Structure</h1>

<pre><code>
📦 app
┣ 📜 main.py
┣ 📁 api
┃ ┗ 📜 routes.py
┣ 📁 adapters
┃ ┗ 📜 vendors.py
┣ 📁 services
┃ ┣ 📜 normalization.py
┃ ┗ 📜 selector.py
┣ 📁 utils
┃ ┣ ⚡ circuit_breaker.py
┃ ┗ 🗄️ redis.py
┣ 📁 core
┃ ┣ ⚙️ config.py
┃ ┗ 🔁 background.py
┣ 📁 models
┃ ┣ 🧩 domain.py
┃ ┗ 📝 request.py

🧪 tests
┣ 📜 conftest.py
┣ 📜 test_api.py
┗ 📜 test_service.py

📄 requirements.txt
</code></pre>
