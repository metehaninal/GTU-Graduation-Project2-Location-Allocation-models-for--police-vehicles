import osmnx as ox
import networkx as nx

PLACE_NAME = "Gaziantep, Türkiye"
FILE_PATH = "./gebze_abstracted.gpkg"

ROAD_FILTER = (
    '["highway"~"motorway|primary|motorway_link|primary_link"]'
)

HIZ_VARSAYIMLARI = {
    'motorway': 120,
    'motorway_link': 80,
    'primary': 100,
    'primary_link': 65,
    'secondary': 80,
    'secondary_link': 50,
    'tertiary': 50,
    'residential': 40
}

TRAFFIC_ESTIMATES = {
    'motorway': 18000,
    'motorway_link': 9000,
    'primary': 4000,
    'primary_link': 2000,
    'secondary': 1500,
    'secondary_link': 1000,
    'tertiary': 800,
    'residential': 500
}

TOLERANCE_METERS = 150 

def create_abstract_network(place, road_filter, filepath, speed_defaults, tolerance):
    print(f"Starting 'Abstraction' process for: {place}...")
    print(f"Tolerance: {tolerance} meters")

    try:
        G = ox.graph_from_place(
            place,
            network_type='drive',
            simplify=True,
            custom_filter=road_filter
        )

        G_proj = ox.project_graph(G)

        G_abstract = ox.consolidate_intersections(
            G_proj,
            tolerance=tolerance,
            rebuild_graph=True,
            dead_ends=False
        )

        components = nx.weakly_connected_components(G_abstract)
        largest_cc = max(components, key=len)
        G_connected = G_abstract.subgraph(largest_cc).copy()

        G_connected = ox.add_edge_speeds(G_connected, hwy_speeds=speed_defaults)
        G_connected = ox.add_edge_travel_times(G_connected)

        for u, v, k, data in G_connected.edges(keys=True, data=True):
            data['travel_time'] = max(0.01, data['travel_time'] / 60.0)

        for node in G_connected.nodes():
            incident_edges = G_connected.edges(node, data=True)
            max_vol = 500

            for u, v, data in incident_edges:
                highway_type = data.get('highway')

                if isinstance(highway_type, list):
                    for h_type in highway_type:
                        vol = TRAFFIC_ESTIMATES.get(h_type, 500)
                        if vol > max_vol:
                            max_vol = vol
                else:
                    vol = TRAFFIC_ESTIMATES.get(highway_type, 500)
                    if vol > max_vol:
                        max_vol = vol

            G_connected.nodes[node]['traffic_volume'] = max_vol

        G_final = ox.project_graph(G_connected, to_crs="EPSG:4326")

        ox.save_graph_geopackage(G_final, filepath=filepath)

        print("SUCCESS")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_abstract_network(
        PLACE_NAME,
        ROAD_FILTER,
        FILE_PATH,
        HIZ_VARSAYIMLARI,
        TOLERANCE_METERS
    )
