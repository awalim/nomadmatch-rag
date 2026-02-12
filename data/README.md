# 🗂️ NomadMatch European Cities Dataset

This directory contains the European cities datasets used for the NomadMatch RAG system.

## 📊 Dataset Files

### 1. `nomadmatch_european_cities.csv` (Main RAG Dataset)
- **Rows:** ~50 European cities
- **Format:** Clean, deduplicated (General tier only)
- **Purpose:** Primary data source for vector embeddings and RAG queries
- **Columns:** City, Country, Region, Cost indices, Internet speeds, Quality scores, etc.

### 2. `nomadmatch_european_cities_with_tiers.csv` (Complete Reference)
- **Rows:** ~150 rows (cities × tiers)
- **Format:** Complete dataset with all data_type values
- **Tiers:** 
  - `General`: Core city data (cost, infrastructure, lifestyle)
  - `Visa`: Visa policies, durations, requirements
  - `Tax`: Tax regimes, benefits, rates
- **Purpose:** Reference and advanced filtering

### 3. `sample_cities.csv` (Testing)
- **Rows:** 10-15 representative cities
- **Purpose:** Quick testing and development

## 🎯 Data Schema

### Core City Attributes
| Column | Description | Example |
|--------|-------------|---------|
| `city` | City name | Lisbon |
| `country` | Country | Portugal |
| `region` | European region | Southern Europe |
| `data_type` | General/Visa/Tax | General |
| `tier` | free/premium | free |

### Cost of Living (EUR/month)
| Column | Description | Scale |
|--------|-------------|-------|
| `Monthly_Budget_Single_EUR` | Single person budget | Very Affordable - Very Expensive |
| `1BR_Center_EUR` | 1-bedroom city center rent | Very Affordable - Very Expensive |
| `Studio_Center_EUR` | Studio city center rent | Very Affordable - Very Expensive |

### Quality Scores (1-10 scale, converted to text)
| Column | Description | Scale |
|--------|-------------|-------|
| `Internet_Reliability_Score` | Internet stability | Very Low - Excellent |
| `Nomad_Community_Score` | DN community size | Very Low - Excellent |
| `Safety_Score` | Safety rating | Very Low - Excellent |
| `English_Proficiency_Score` | English speaking level | Very Low - Excellent |

### Environmental
| Column | Description | Scale |
|--------|-------------|-------|
| `Summer_Temperature` | Summer climate | Cool - Very Hot |
| `Winter_Temperature` | Winter climate | Very Cold - Warm |
| `Sunshine_Level` | Annual sunshine | Low - Very High |
| `Rainfall_Level` | Precipitation | Very Dry - Very Rainy |

### Infrastructure
| Column | Description | Scale |
|--------|-------------|-------|
| `Coworking_Availability` | Coworking spaces | Very Few - Abundant |
| `Public_Transport_Score` | Transit quality | Very Low - Excellent |
| `Internet_Avg_Mbps` | Internet speed | Range in Mbps |

### Visa & Tax (Tiered data)
| Column | Description | Details |
|--------|-------------|---------|
| `Digital_Nomad_Visa` | Availability | Yes/No |
| `Visa_Duration` | Visa length | Short/Medium/Long-term |
| `Visa_Type_Details` | Specific visa | D7/D8, Zivno, etc. |
| `Tax_Level` | Tax burden | Very Low - Very High |
| `Tax_Benefits_Premium` | Special regimes | NHR, Beckham Law, etc. |

## 🚀 Usage Examples

### Basic RAG Query
```python
# Find cities with good internet and affordable cost
query = "Show me cities with excellent internet and moderate rent"
