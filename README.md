# CumulativeCorr

**CumulativeCorr** is a Streamlit-based application for cumulative correlation analysis of paired stable-isotope data through a stratigraphic section.

It is designed for datasets containing:

- stratigraphic level measured from the base of the studied interval (m)
- d13C
- d18O

CumulativeCorr calculates cumulative **Pearson correlation coefficients** and **Spearman rank correlation coefficients**, together with their p-values and sample sizes.

## Author

Created by **Myung-Jun Seo**

Collaboration is welcome.  
Contact: **mseo2@crimson.ua.edu**

## Analysis modes

CumulativeCorr provides two cumulative analysis directions:

- **Downward cumulative** — starts at the uppermost sample and progressively includes samples downward through the section.
- **Upward cumulative** — starts at the lowermost sample and progressively includes samples upward through the section.

Missing values can be handled by pairwise deletion or by stopping the cumulative calculation at the first missing value.

## Requirements

CumulativeCorr v1.0.0 was tested with:

- Python 3.14.7
- numpy 2.5.3
- pandas 3.0.6
- streamlit 1.64.0
- altair 6.3.0
- scipy 1.18.1

The exact Python package requirements are listed in `requirements.txt`.

## Running from source

1. Install Python 3.14.7 or a compatible Python version.

2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Run:

```bash
python run_app.py
```

The Streamlit application should open automatically in the default web browser.

Alternatively, the application can be launched directly with:

```bash
streamlit run app.py
```

## Input

Paste tabular data into the application using the following variables:

- `level_m_from_base`
- `d13C`
- `d18O`

Stratigraphic level must be measured in meters from the base of the studied interval. The order of rows does not matter, provided that each stratigraphic level is correctly paired with its corresponding δ13C and δ18O values.

The minimum number of paired observations required before correlation statistics are calculated can be selected in the interface.

## Output

For each cumulative step, the application reports:

- cumulative stratigraphic distance
- number of paired observations (`n`)
- Pearson correlation coefficient (`r`)
- Pearson p-value
- Spearman rank correlation coefficient (`rho`)
- Spearman p-value

Results are displayed as a table and an interactive Altair chart.

## Building the Windows release

The Windows executable can be built with PyInstaller using:

```bash
python -m PyInstaller --noconfirm --clean --onedir --windowed --name CumulativeCorr --icon "CCorr.ico" --add-data "app.py;." --collect-all streamlit --collect-all altair run_app.py
```

The generated application will be placed in:

```text
dist/CumulativeCorr/
```

The executable and the `_internal` folder must remain together.

## Version

This repository documents **CumulativeCorr v1.0.0**, the version archived for the associated research publication.

## Citation

Citation metadata are provided in `CITATION.cff`.

A permanent software DOI will be added after archival in Zenodo.

## License

CumulativeCorr is released under the **MIT License**. See `LICENSE`.
