# Salesforce Data Enrichment Script (Python)

## Overview

This repository contains the Python/Selenium script used for the data enrichment part of the Salesforce developer assignment.

Its purpose is to scrape the `azcarecheck.azdhs.gov` website to find the "Chief Administrative Officer" for each facility in the Arizona (AZ) dataset. It generates an enriched CSV file tailored for import into the Salesforce org as a Static Resource.


## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone [YOUR_REPO_URL]
    cd [YOUR_REPO_NAME]
    ```

2.  **Prepare Input Data:**
    Ensure the filtered source file, `NH_ProviderInfo_Sep2025 - filtered.csv`, is in the same directory as the script.

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the script from your terminal:

```bash
python script.py