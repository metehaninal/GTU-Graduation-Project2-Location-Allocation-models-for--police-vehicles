import streamlit as st
import geopandas as gpd
import networkx as nx
import osmnx as ox
import pulp
import folium
import streamlit.components.v1 as components
import random
import time
import pandas as pd

st.set_page_config(layout="wide", page_title="Police Patrol Optimization")

def solve_model_1_exact(locations, p_vehicles, traffic_volumes, coverage_sets):
    model = pulp.LpProblem("Model_1", pulp.LpMaximize)
    x = pulp.LpVariable.dicts("x", locations, cat='Binary')
    z = {i: pulp.LpVariable.dicts(f"z_{i}", coverage_sets[i], cat='Binary') for i in locations}
    
    model += pulp.lpSum(traffic_volumes[j] * x[j] for j in locations)
    model += pulp.lpSum(x[j] for j in locations) == p_vehicles
    
    for i in locations:
        model += pulp.lpSum(z[i][j] for j in coverage_sets[i]) == 1
    for i in locations:
        for j in coverage_sets[i]:
            model += z[i][j] <= x[j]
            
    model.solve(pulp.PULP_CBC_CMD(msg=False))
    
    if pulp.LpStatus[model.status] == 'Optimal':
        chosen = [j for j in locations if x[j].varValue == 1]
        val = pulp.value(model.objective)
        return 'Optimal', chosen, val
    return 'Infeasible', [], 0

def solve_model_2_exact(locations, p_vehicles, traffic_volumes, coverage_sets, shift_len, event_time, travel_time, model_name="Model_2"):
    model = pulp.LpProblem(model_name, pulp.LpMaximize)
    x = pulp.LpVariable.dicts("x", locations, cat='Binary')
    z = {i: pulp.LpVariable.dicts(f"z_{i}", coverage_sets[i], cat='Binary') for i in locations}
    
    term1 = pulp.lpSum(shift_len * traffic_volumes[j] * x[j] for j in locations)
    term2 = pulp.lpSum((travel_time[i][j] + event_time[i]) * traffic_volumes[j] * z[i][j] 
                       for i in locations for j in coverage_sets[i])
    
    model += term1 - term2
    model += pulp.lpSum(x[j] for j in locations) == p_vehicles
    
    for i in locations:
        model += pulp.lpSum(z[i][j] for j in coverage_sets[i]) == 1
    for i in locations:
        for j in coverage_sets[i]:
            model += z[i][j] <= x[j]
            
    model.solve(pulp.PULP_CBC_CMD(msg=False))
    
    if pulp.LpStatus[model.status] == 'Optimal':
        chosen = [j for j in locations if x[j].varValue == 1]
        val = pulp.value(model.objective)
        return 'Optimal', chosen, val
    return 'Infeasible', [], 0

def solve_model_3_exact(locations, p_vehicles, traffic_volumes, coverage_sets, shift_len, event_time, travel_time):
    return solve_model_2_exact(locations, p_vehicles, traffic_volumes, coverage_sets, shift_len, event_time, travel_time, model_name="Model_3")

def solve_model_4_exact(locations, p_vehicles, traffic_volumes, coverage_sets, shift_len, event_time, travel_time):
    shifts = [1, 2, 3]
    model = pulp.LpProblem("Model_4_Joint", pulp.LpMaximize)
    
    x = pulp.LpVariable.dicts("x", (locations, shifts), cat='Binary')
    z = {f: {i: pulp.LpVariable.dicts(f"z_{i}_s{f}", coverage_sets[i], cat='Binary')
             for i in locations} for f in shifts}
    u = pulp.LpVariable.dicts("u", locations, lowBound=0, cat='Continuous')

    obj_terms = []
    for f in shifts:
        for j in locations:
            obj_terms.append(shift_len * traffic_volumes[j] * x[j][f])
        for i in locations:
            for j in coverage_sets[i]:
                obj_terms.append(-(travel_time[i][j] + event_time[i]) * traffic_volumes[j] * z[f][i][j])

    sorted_vols = sorted(traffic_volumes.values(), reverse=True)
    top_p_sum = sum(sorted_vols[:p_vehicles])
    gross_upper_bound = shift_len * top_p_sum
    penalty_weight = gross_upper_bound + 1000
    
    model += pulp.lpSum(obj_terms) - penalty_weight * pulp.lpSum(u[j] for j in locations)
    
    for f in shifts:
        model += pulp.lpSum(x[j][f] for j in locations) == p_vehicles
        for i in locations:
            model += pulp.lpSum(z[f][i][j] for j in coverage_sets[i]) == 1
            for j in coverage_sets[i]:
                model += z[f][i][j] <= x[j][f]
                
    for j in locations:
        model += u[j] >= pulp.lpSum(x[j][f] for f in shifts) - 1

    model.solve(pulp.PULP_CBC_CMD(msg=False))
    
    if pulp.LpStatus[model.status] == 'Optimal':
        total_reuse_amount = 0
        reused_sites_count = 0
        for j in locations:
            if u[j].varValue and u[j].varValue > 1e-6:
                total_reuse_amount += u[j].varValue
                reused_sites_count += 1
                
        val = pulp.value(model.objective) + (total_reuse_amount * penalty_weight)
        
        shifts_data = {f: [] for f in shifts}
        all_chosen = []
        for f in shifts:
            for j in locations:
                if x[j][f].varValue == 1:
                    shifts_data[f].append(j)
                    all_chosen.append(j)
        
        return 'Optimal', {
            'unique': list(set(all_chosen)),
            'shifts': shifts_data,
            'reuse_stats': {'count': reused_sites_count, 'amount': total_reuse_amount}
        }, val
    
    return 'Infeasible', {'unique': [], 'shifts': {f: [] for f in shifts}, 'reuse_stats': {'count': 0, 'amount': 0}}, 0

@st.cache_data
def load_data(filepath):
    nodes = gpd.read_file(filepath, layer="nodes").set_index('osmid')
    edges = gpd.read_file(filepath, layer="edges").set_index(['u', 'v', 'key'])
    return nodes, edges, ox.graph_from_gdfs(nodes, edges)

@st.cache_data
def generate_simulation_data(locations, seed=42):
    random.seed(seed)
    return (
        {n: random.randint(500, 3000) for n in locations},
        {n: random.uniform(0.25, 1.0) for n in locations},
        {n: (10 if random.choice([True, False]) else 20) for n in locations}
    )

def clean_common_islands(locations, set_std, set_prio):
    iso = {i for i in locations if not set_std[i] or not set_prio[i]}
    return [i for i in locations if i not in iso], iso

def filter_data_for_active(active_locs, all_iso, coverage_sets, traffic_vols, extra_dicts=[]):
    for node in all_iso:
        coverage_sets.pop(node, None)
        traffic_vols.pop(node, None)
        for d in extra_dicts:
            d.pop(node, None)
    for loc in active_locs:
        coverage_sets[loc] = [j for j in coverage_sets[loc] if j not in all_iso]
        for d in extra_dicts:
            if isinstance(d.get(loc), dict):
                for k in list(d[loc].keys()):
                    if k in all_iso:
                        del d[loc][k]
    return coverage_sets, traffic_vols
