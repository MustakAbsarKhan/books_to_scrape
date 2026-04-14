---

# 📚 Async Books Scraper

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Asyncio](https://img.shields.io/badge/Asyncio-Concurrent%20Scraping-green)
![aiohttp](https://img.shields.io/badge/aiohttp-HTTP%20Client-orange)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-HTML%20Parsing-yellow)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-success)

---

## 🚀 Overview

This project is a **high-performance asynchronous web scraper** built using Python.

It scrapes book data from:

👉 [https://books.toscrape.com/](https://books.toscrape.com/)

and demonstrates **real-world production scraping techniques**, including:

* Async concurrency (aiohttp + asyncio)
* Dynamic rate limiting
* Adaptive delay control
* Anti-blocking strategies
* Structured data extraction
* CSV export pipeline

---

## ⚙️ Features

### ⚡ High Performance

* Async / concurrent scraping using `aiohttp`
* Semaphore-based request control
* Parallel product page scraping

### 🧠 Smart Adaptation System

* Dynamic concurrency adjustment
* Adaptive delay based on:

  * response speed
  * server blocking (403 / 429)
* Self-healing scraper behavior

### 🛡️ Anti-Blocking Techniques

* User-Agent rotation support
* Controlled request pacing
* Human-like delays

### 📦 Data Pipeline

* Structured data extraction
* Clean dataset formatting
* CSV export (Excel / pandas ready)

### 📊 Extracted Fields

Each product contains:

* Title
* Category
* Price
* Rating
* Stock availability
* UPC
* Description
* Product URL

---

## 🧱 Tech Stack

| Technology    | Purpose           |
| ------------- | ----------------- |
| Python        | Core language     |
| asyncio       | Async concurrency |
| aiohttp       | HTTP requests     |
| BeautifulSoup | HTML parsing      |
| csv           | Data export       |
| urllib        | URL handling      |

---

## 📁 Project Structure

```text
async-books-scraper/
│
├── scraper.py          # Main scraper logic
├── books.csv           # Output dataset (generated)
├── README.md           # Documentation
```

---

## ⚙️ How It Works

### 1️⃣ Crawl catalogue pages

The scraper starts from:

```
https://books.toscrape.com/
```

It extracts:

* product URLs
* basic metadata

---

### 2️⃣ Concurrent product scraping

All product pages are scraped in parallel using:

* asyncio.gather()
* semaphore control

---

### 3️⃣ Adaptive intelligence layer

The scraper automatically adjusts:

* 🐢 slows down if errors increase
* 🚀 speeds up if stable
* 🧠 adjusts delay based on response time

---

### 4️⃣ Data export

All data is stored and exported as:

```
books.csv
```

---

## 🧠 Key Concepts Demonstrated

* Async programming in Python
* Web scraping architecture
* Rate limiting strategies
* Real-world crawler design
* Data pipeline construction

---

## 📊 Example Output

| Title                | Price  | Rating | Stock    |
| -------------------- | ------ | ------ | -------- |
| A Light in the Attic | £51.77 | Three  | In stock |

---

## 🚀 Installation

```bash
git clone https://github.com/yourusername/async-books-scraper.git
cd async-books-scraper
pip install -r requirements.txt
```

---

## ▶️ Run the scraper

```bash
python scraper.py
```

---

## 📦 Requirements

```text
aiohttp
beautifulsoup4
lxml
```

Install with:

```bash
pip install aiohttp beautifulsoup4 lxml
```

---

## 📈 Performance Highlights

* ⚡ 5–20x faster than blocking scrapers
* 🔄 Auto-adjusts to server conditions
* 🧠 Handles failures gracefully
* 📉 Minimizes blocking risk

---

## 🧑‍💻 Author

**Mohammad Mustak Absar Khan**

* 💻 Python Developer
* 🧠 Interested in scraping, automation, AI systems

---

## ⭐ If you like this project

If this project helped you understand async scraping:

⭐ Star the repo
🍴 Fork it
🚀 Build on top of it

---

## 📜 License

This project is licensed under the MIT License.

---