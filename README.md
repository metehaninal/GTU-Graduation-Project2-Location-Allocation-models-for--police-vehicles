# GTU Graduation Project 2  
## Location-Allocation Models for Police Patrol Vehicles

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18213336.svg)](https://doi.org/10.5281/zenodo.18213336)

This repository contains the source code and experimental implementation developed as part of a **Graduation Project II- CSE496** at **Gebze Technical University, Department of Computer Engineering**.

The project focuses on **location-allocation optimization models for police patrol vehicles** on a road network, aiming to improve patrol visibility, coverage, and response efficiency.

---

## 🎓 Academic Information

- **University:** Gebze Technical University  
- **Department:** Computer Engineering  
- **Course:** Graduation Project II  

### 👨‍🏫 Supervisor  
- **Prof. Dr. Didem GÖZÜPEK**

### 👨‍🎓 Authors  
- **Metehan İnal**  
- **Yiğit Karaduman**

---

## 📄 Related Publication

This project is inspired by and based on the following academic study:

**Adler, N., Hakkert, A. S., Kornbluth, J., Raviv, T., & Sher, M.**  
*Location-allocation models for traffic police patrol vehicles on an interurban network*  
Annals of Operations Research, 221, 9–31 (2014).  
DOI: https://doi.org/10.1007/s10479-012-1275-2

The original paper proposes a set of integer linear programming models for the optimal allocation of routine patrol vehicles (RPVs) over a road network.  
This project implements, adapts, and experimentally evaluates these models using modern open-source tools.

---

## 🎯 Project Objective

The main objectives of this graduation project are:

- To model the **optimal placement of police patrol vehicles** on a road network  
- To ensure **full network coverage** under legal response-time constraints  
- To maximize **police presence and visibility** based on traffic intensity  
- To evaluate **multi-shift and dynamic deployment strategies**  
- To provide a **reproducible and extensible implementation** of the proposed models  

---

## 🧠 Implemented Optimization Models

The following four Integer Linear Programming (ILP) models are implemented:

### 🔹 Model 1 – Conspicuous-Coverage Trade-off Model  
Maximizes patrol visibility based on traffic volume while guaranteeing full coverage of the road network.

### 🔹 Model 2 – Maximum Conspicuousness with Calls-for-Service  
Extends Model 1 by incorporating travel times and incident-handling durations.

### 🔹 Model 3 – Priority-Based Coverage Model  
Introduces differentiated response time requirements for high-priority road segments.

### 🔹 Model 4 – Multi-Shift Location-Allocation Model  
Allocates patrol vehicles dynamically across multiple shifts while limiting repeated use of the same locations to model deterrence (halo effect).

---

## 🗺️ Road Network Abstraction and Data Preparation

- Road network data is retrieved from **OpenStreetMap** using the `osmnx` library.
- Intersections are consolidated to generate an abstracted graph representation.
- Speed and traffic volume assumptions are assigned based on road classifications.
- Travel times are computed and embedded into the optimization models.
- The largest connected component of the network is retained to ensure feasibility.

---

## 🧪 Repository Structure

```text
.
├── absdataset.py      # Road network abstraction and preprocessing
├── interface.py       # Optimization models and Streamlit-based interface
├── README.md          # Project documentation

## ⚙️ Technologies & Tools 

- **Python 3**
- **PuLP** (Integer Linear Programming)
- **NetworkX**
- **OSMnx**
- **GeoPandas**
- **Streamlit**
- **Folium**

---

## 🚀 How to Run the Project 

### 1️⃣ Install Dependencies
```bash
pip install osmnx networkx geopandas pulp streamlit folium
python absdataset.py
streamlit run interface.py
