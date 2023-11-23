import pypsa
import pandas as pd
from dataclasses import dataclass


climatic_year = 2000
time_horizon_in_hours = 365 * 24
network = pypsa.Network()

def add_scandinavia(network: pypsa.Network(), climatic_year: int, time_horizon_in_hours: int):
    country = "scandinavia"
    full_demand = pd.read_csv("./data/demand_2030_Scandinavia.csv", sep=";", index_col=1, parse_dates=True).groupby(pd.Grouper(key="climatic_year"))
    full_wind_on_shore = pd.read_csv("./data/capa_factor_2030_Scandinavia_onshore.csv", index_col=1, parse_dates=True, sep=";").groupby(pd.Grouper(key="climatic_year"))
    full_solar = pd.read_csv("./data/capa_factor_2030_Scandinavia_solar.csv", index_col=1, parse_dates=True, sep=";").groupby(pd.Grouper(key="climatic_year"))
    full_wind_off_shore = pd.read_csv("./data/capa_factor_2030_Scandinavia_offshore.csv", index_col=1, parse_dates=True, sep=";").groupby(pd.Grouper(key="climatic_year"))

    

    demand = full_demand.get_group(climatic_year)
    solar = full_solar.get_group(climatic_year)
    wind_on_shore = full_wind_on_shore.get_group(climatic_year)
    wind_off_shore = full_wind_off_shore.get_group(climatic_year)
    
    network.snapshots = demand.index[0:time_horizon_in_hours]
    
    network.add("Bus", name="Scandinavia", x=15.255119, y=60.128161)
    
    coal_marginal_costs = 160
    gas_marginal_costs = 120
    oil_marginal_costs = 100
    nuclear_marginal_costs = 10
    hydro_marginal_costs = 5
    wind_marginal_costs = 5
    solar_marginal_costs = 5
    biomass_marginal_costs = 5


    reservoir_max_hours = 365*24
    pumped_max_hours = 100
    battery_max_hours = 200
    H2_max_hours = 300
    
    generators = [
    {"name": f"{country}Fossils", "carrier": "Fossils", "p_nom": 5000, "p_min_pu": 0, "p_max_pu": 1, "marginal_cost": gas_marginal_costs, "efficiency": 0.4,
     "committable": True, "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}BioEnergies", "carrier": "BioEnergies", "p_nom":11000, "p_min_pu": 0, "p_max_pu": 1, "marginal_cost": biomass_marginal_costs, "efficiency": 0.5, 
     "committable": True, "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Hydroelectric", "carrier":"Hydro", "p_nom": 57000, "p_min_pu": 0, "p_max_pu": 1, "marginal_cost": hydro_marginal_costs, "efficiency": 1, "committable": True,
     "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Wind_on_shore", "carrier": "Wind_on_shore", "p_nom": 43000, "p_min_pu":wind_on_shore.value, "p_max_pu": wind_on_shore.value, "marginal_cost": wind_marginal_costs, "efficiency":1, "committable": False,
     "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Wind_off_shore", "carrier": "Wind_off_shore", "p_nom": 17000, "p_min_pu":wind_off_shore.value, "p_max_pu": wind_off_shore.value, "marginal_cost": wind_marginal_costs, "efficiency":1, "committable": False,
     "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Nuclear", "carrier": "Nuclear", "p_nom": 11000, "p_min_pu":0, "p_max_pu": 1, "marginal_cost": nuclear_marginal_costs, "efficiency":1, "committable": True,
     "min_up_time": 24, "min_down_time": 24},
    {"name": f"{country}Solar", "carrier": "Solar", "p_nom": 19000, "p_min_pu":solar.value, "p_max_pu": solar.value, "marginal_cost": solar_marginal_costs, "efficiency":1, "committable": False,
     "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Failure", "carrier": "Failure", "p_nom": 100000, "p_min_pu":0, "p_max_pu": 1, "marginal_cost": 100000, "efficiency":1, "committable": True,
     "min_up_time": 1, "min_down_time": 1}
]
    
    storage_units = [
        {"name": f"{country}Reservoir", "carrier": "Reservoir", "p_nom": 100000, "p_min_pu": 0, "p_max_pu": 1, "max_hours": reservoir_max_hours, "efficiency": 1, "cyclic_state_of_charge": True, "p_nom_discharge" : 100, "p_nom_charge" : 100},
        {"name": f"{country}Pumped", "carrier": "Pumped", "p_nom": 100000, "p_min_pu": 0, "p_max_pu": 1, "max_hours": pumped_max_hours, "efficiency": 1, "cyclic_state_of_charge": True, "p_nom_discharge" : 100, "p_nom_charge" : 100},
        {"name": f"{country}Battery", "carrier": "Battery", "p_nom": 100000, "p_min_pu": 0, "p_max_pu": 1, "max_hours": battery_max_hours, "efficiency": 1, "cyclic_state_of_charge": True, "p_nom_discharge" : 100, "p_nom_charge" : 100},
        {"name": f"{country}H2", "carrier": "H2", "p_nom": 100000, "p_min_pu": 0, "p_max_pu": 1, "max_hours": H2_max_hours, "efficiency": 1, "cyclic_state_of_charge": True, "p_nom_discharge" :100, "p_nom_charge" : 100},
]
    
    for generator in generators:
        network.add("Generator", bus="Scandinavia", **generator,)
    

    for storage in storage_units:
        network.add("Store", bus="Scandinavia", **storage,)


    loads = [
    {"name": f"{country}-load", "bus": "Scandinavia", "carrier": "AC","p_set": demand[0:time_horizon_in_hours]["value"].values*1},
    {"name": f"{country}Curtailment-load", "bus": "Curtailment", "carrier": "AC","p_set": 10000},
]
    
    for load in loads:
        network.add("Load", **load)
        





def add_germany(network: pypsa.Network(), climatic_year: int, time_horizon_in_hours: int):
    country = "germany"
    full_demand = pd.read_csv("./data/demand_2030_Germany.csv", sep=";", index_col=1, parse_dates=True).groupby(pd.Grouper(key="climatic_year"))
    full_wind_on_shore = pd.read_csv("./data/capa_factor_2030_Germany_onshore.csv", index_col=1, parse_dates=True, sep=";").groupby(pd.Grouper(key="climatic_year"))
    full_solar = pd.read_csv("./data/capa_factor_2030_Germany_solar.csv", index_col=1, parse_dates=True, sep=";").groupby(pd.Grouper(key="climatic_year"))
    full_wind_off_shore = pd.read_csv("./data/capa_factor_2030_Germany_offshore.csv", index_col=1, parse_dates=True, sep=";").groupby(pd.Grouper(key="climatic_year"))

    

    demand = full_demand.get_group(climatic_year)
    solar = full_solar.get_group(climatic_year)
    wind_on_shore = full_wind_on_shore.get_group(climatic_year)
    wind_off_shore = full_wind_off_shore.get_group(climatic_year)
    
    network.snapshots = demand.index[0:time_horizon_in_hours]
    
    network.add("Bus", name="Germany",  x=13.4105300, y=52.5243700)
    
    coal_marginal_costs = 160
    gas_marginal_costs = 120
    oil_marginal_costs = 100
    nuclear_marginal_costs = 10
    hydro_marginal_costs = 5
    wind_marginal_costs = 5
    solar_marginal_costs = 5
    biomass_marginal_costs = 5


    reservoir_max_hours = 365*24
    pumped_max_hours = 100
    battery_max_hours = 200
    H2_max_hours = 300
    
    generators = [
    {"name": f"{country}Fossils", "carrier": "Fossils", "p_nom": 5000, "p_min_pu": 0, "p_max_pu": 1, "marginal_cost": gas_marginal_costs, "efficiency": 0.4,
     "committable": True, "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}BioEnergies", "carrier": "BioEnergies", "p_nom":11000, "p_min_pu": 0, "p_max_pu": 1, "marginal_cost": biomass_marginal_costs, "efficiency": 0.5, 
     "committable": True, "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Hydroelectric", "carrier":"Hydro", "p_nom": 57000, "p_min_pu": 0, "p_max_pu": 1, "marginal_cost": hydro_marginal_costs, "efficiency": 1, "committable": True,
     "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Wind_on_shore", "carrier": "Wind_on_shore", "p_nom": 43000, "p_min_pu":wind_on_shore.value, "p_max_pu": wind_on_shore.value, "marginal_cost": wind_marginal_costs, "efficiency":1, "committable": False,
     "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Wind_off_shore", "carrier": "Wind_off_shore", "p_nom": 17000, "p_min_pu":wind_off_shore.value, "p_max_pu": wind_off_shore.value, "marginal_cost": wind_marginal_costs, "efficiency":1, "committable": False,
     "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Nuclear", "carrier": "Nuclear", "p_nom": 11000, "p_min_pu":0, "p_max_pu": 1, "marginal_cost": nuclear_marginal_costs, "efficiency":1, "committable": True,
     "min_up_time": 24, "min_down_time": 24},
    {"name": f"{country}Solar", "carrier": "Solar", "p_nom": 19000, "p_min_pu":solar.value, "p_max_pu": solar.value, "marginal_cost": solar_marginal_costs, "efficiency":1, "committable": False,
     "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Failure", "carrier": "Failure", "p_nom": 100000, "p_min_pu":0, "p_max_pu": 1, "marginal_cost": 100000, "efficiency":1, "committable": True,
     "min_up_time": 1, "min_down_time": 1}
]
    
    storage_units = [
        {"name": f"{country}Reservoir", "carrier": "Reservoir", "p_nom": 100000, "p_min_pu": 0, "p_max_pu": 1, "max_hours": reservoir_max_hours, "efficiency": 1, "cyclic_state_of_charge": True, "p_nom_discharge" : 100, "p_nom_charge" : 100},
        {"name": f"{country}Pumped", "carrier": "Pumped", "p_nom": 100000, "p_min_pu": 0, "p_max_pu": 1, "max_hours": pumped_max_hours, "efficiency": 1, "cyclic_state_of_charge": True, "p_nom_discharge" : 100, "p_nom_charge" : 100},
        {"name": f"{country}Battery", "carrier": "Battery", "p_nom": 100000, "p_min_pu": 0, "p_max_pu": 1, "max_hours": battery_max_hours, "efficiency": 1, "cyclic_state_of_charge": True, "p_nom_discharge" : 100, "p_nom_charge" : 100},
        {"name": f"{country}H2", "carrier": "H2", "p_nom": 100000, "p_min_pu": 0, "p_max_pu": 1, "max_hours": H2_max_hours, "efficiency": 1, "cyclic_state_of_charge": True, "p_nom_discharge" :100, "p_nom_charge" : 100},
]
    
    for generator in generators:
        network.add("Generator", bus="Germany", **generator,)
    

    for storage in storage_units:
        network.add("Store", bus="Germany", **storage,)


    loads = [
    {"name": f"{country}-load", "bus": "Germany", "carrier": "AC","p_set": demand[0:time_horizon_in_hours]["value"].values*1},
    {"name": f"{country}Curtailment-load", "bus": "Curtailment", "carrier": "AC","p_set": 10000},
]
    
    for load in loads:
        network.add("Load", **load)
        
        
        
        
        
        
        