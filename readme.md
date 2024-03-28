# Streaming Platform Catalog Analysis

## Overview
This project aims to investigate the content, casting, directory, and duration of movies in streaming platform catalogs to identify the characteristics of an average movie in recent times. By analyzing these aspects, we aim to understand the baseline features of movies that are prevalent in streaming services today.

## Purpose and Scope
The analysis focuses on examining the streaming platforms' catalogs to provide insights into:
- The distribution of movie production years, highlighting the prevalence of recent productions.
- Casting size, identifying the average number of people involved.
- The average duration of movies, providing a sense of typical movie length.

## Data Sources
The analysis utilizes the following data sources:
- **CSV Files:** Two CSV files located in the `Data` folder, containing detailed information about the movies available on various streaming platforms.
- **SQL Script:** A SQL script titled `Table_Creation`, found in the `Database` folder, is used to structure the data appropriately for analysis.
- **Jupyter Notebook:** The `Tables_Creation.ipynb` notebook is used for scraping the CSV files and fulfilling the database tables according to the structure defined by the SQL script.
- **Jupyter Notebook:** The `Data_Analyze.ipynb` notebook is used to create the analyze from the database and create the visuals necessary for presentation.

## Key Findings
- The catalog primarily features movies from **recent productions**, indicating a focus on contemporary content by streaming services.
- The **average casting size** is found to be around 6 to 7 individuals, suggesting a standard group size for movie productions.
- The **average duration** of movies is approximately 1 hour and 40 minutes, offering insight into the preferred movie length for streaming platforms' audiences.

## Requirements
Specific Python libraries or dependencies required for running the analysis are outlined in a separate `.in` file, ensuring that the environment setup is straightforward and replicable.

## Conclusion
The analyze demostrate that platforms are most focused in original content and recently ones instead of old content from publishers. It was possible to identify an average casting size and duration to help identify a baseline for an avarage movie creation.