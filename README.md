# LinkedIn Counter Pagination Bot 🚀

Automates messaging 1st-degree LinkedIn connections from a specific
company using Selenium with a counter-based pagination system.

⚠️ Educational purposes only. May violate LinkedIn Terms of Service. Use
responsibly.

------------------------------------------------------------------------

## ✨ Features

-   Automated LinkedIn login
-   Filters 1st-degree connections by company
-   Sends messages directly from search results
-   Counter-based pagination logic
-   Resume-safe restart support (`START_FROM`)
-   Human-like random delays
-   Dynamic element handling

------------------------------------------------------------------------

## 🧠 Counter-Based Pagination Logic

Instead of clicking "Next Page", the bot calculates:

Page = ((counter - 1) // 10) + 1\
Position = (counter - 1) % 10

This ensures: - No duplicate messaging - Precise resume capability -
Sequential connection targeting

------------------------------------------------------------------------

## 🛠 Tech Stack

-   Python 3
-   Selenium WebDriver
-   ChromeDriver

------------------------------------------------------------------------

## ⚙️ Setup

Install dependency:

pip install selenium

Download matching ChromeDriver version and add to PATH.

------------------------------------------------------------------------

## 🔧 Configuration

Edit inside `main()`:

LINKEDIN_EMAIL = "your_email"\
LINKEDIN_PASSWORD = "your_password"\
COMPANY_NAME = "Company Name"\
MAX_MESSAGES = 20\
START_FROM = 1

------------------------------------------------------------------------

## ⚠️ Disclaimer

This project is intended for automation learning and Selenium practice.

The author is not responsible for account restrictions or bans. Use at
your own risk.
