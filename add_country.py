import pypsa
import pandas as pd
from dataclasses import dataclass
import numpy as np


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
    nuclear_marginal_costs = 40
    hydro_marginal_costs = 2
    wind_marginal_costs = 1
    solar_marginal_costs = 3
    biomass_marginal_costs = 10

    reservoir_max_hours = 365*24
    pumped_max_hours = 100
    battery_max_hours = 200
    H2_max_hours = 300
    
    generators = [
    {"name": f"{country}Gas", "carrier": "Gas", "p_nom": 5000, "p_min_pu": 0, "p_max_pu": 1, "marginal_cost": gas_marginal_costs, "efficiency": 0.4,
     "committable": False, "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}BioEnergies", "carrier": "BioEnergies", "p_nom":11000, "p_min_pu": 0, "p_max_pu": 1, "marginal_cost": biomass_marginal_costs, "efficiency": 0.5, 
     "committable": False, "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Hydroelectric", "carrier":"Hydro", "p_nom": 57000, "p_min_pu": 0, "p_max_pu": 1, "marginal_cost": hydro_marginal_costs, "efficiency": 1, "committable": False,
     "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Wind_on_shore", "carrier": "Wind_on_shore", "p_nom": 43000, "p_min_pu":0, "p_max_pu": wind_on_shore.value, "marginal_cost": wind_marginal_costs, "efficiency":1, "committable": False,
     "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Wind_off_shore", "carrier": "Wind_off_shore", "p_nom": 17000, "p_min_pu":0, "p_max_pu": wind_off_shore.value, "marginal_cost": wind_marginal_costs, "efficiency":1, "committable": False,
     "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Nuclear", "carrier": "Nuclear", "p_nom": 11000, "p_min_pu":0, "p_max_pu": 1, "marginal_cost": nuclear_marginal_costs, "efficiency":1, "committable": False,
     "min_up_time": 24, "min_down_time": 24},
    {"name": f"{country}Solar", "carrier": "Solar", "p_nom": 19000, "p_min_pu":0, "p_max_pu": solar.value, "marginal_cost": solar_marginal_costs, "efficiency":1, "committable": False,
     "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Failure", "carrier": "Failure", "p_nom": 100000, "p_min_pu":0, "p_max_pu": 1, "marginal_cost": 1000, "efficiency":1, "committable": False,
     "min_up_time": 1, "min_down_time": 1}
]
    
    storage_units = [
        {"name": f"{country}Reservoir", "carrier": "Reservoir", "p_nom": 10000, "p_min_pu": 0, "p_max_pu": 1, "max_hours": reservoir_max_hours, "efficiency": 1, "cyclic_state_of_charge": True, "p_nom_discharge" : 100, "p_nom_charge" : 100},
        {"name": f"{country}Pumped", "carrier": "Pumped", "p_nom": 1000, "p_min_pu": 0, "p_max_pu": 1, "max_hours": pumped_max_hours, "efficiency": 1, "cyclic_state_of_charge": True, "p_nom_discharge" : 100, "p_nom_charge" : 100},
        {"name": f"{country}Battery", "carrier": "Battery", "p_nom": 500, "p_min_pu": 0, "p_max_pu": 1, "max_hours": battery_max_hours, "efficiency": 1, "cyclic_state_of_charge": True, "p_nom_discharge" : 100, "p_nom_charge" : 100},
        {"name": f"{country}H2", "carrier": "H2", "p_nom": 0, "p_min_pu": 0, "p_max_pu": 1, "max_hours": H2_max_hours, "efficiency": 1, "cyclic_state_of_charge": True, "p_nom_discharge" :100, "p_nom_charge" : 100},
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
    
    full_demand = pd.read_csv("./data/demand_2030_Germany.csv", sep=";", index_col=1, parse_dates=True).groupby(pd.Grouper(key="climatic_year"))
    full_wind_on_shore = pd.read_csv("./data/capa_factor_2030_Germany_onshore.csv", index_col=1, parse_dates=True, sep=";").groupby(pd.Grouper(key="climatic_year"))
    full_solar = pd.read_csv("./data/capa_factor_2030_Germany_solar.csv", index_col=1, parse_dates=True, sep=";").groupby(pd.Grouper(key="climatic_year"))
    full_wind_off_shore = pd.read_csv("./data/capa_factor_2030_Germany_offshore.csv", index_col=1, parse_dates=True, sep=";").groupby(pd.Grouper(key="climatic_year"))

    demand = full_demand.get_group(climatic_year)
    wind_on_shore = full_wind_on_shore.get_group(climatic_year)
    wind_off_shore = full_wind_off_shore.get_group(climatic_year)
    solar_pv = full_solar.get_group(climatic_year)
    
    network.snapshots = demand.index[0:time_horizon_in_hours]
    
    network.add("Bus", name="Germany", x=13.404954, y=52.520008)
    
    @dataclass
    class FuelSources:
        name: str
        co2_emissions: float
        committable: bool
        min_up_time: float
        min_down_time: float
        primary_cost: float = None  # € / MWh (multiply this by the efficiency of your power plant to get the marginal cost)

        def return_as_dict(self, keys):
            return {key: self.__dict__[key] for key in keys}

        def carrier_characteristics(self):
            return self.return_as_dict(["name", "co2_emissions"])

        def generator_characteristics(self):
            return self.return_as_dict(["committable", "min_up_time", "min_down_time"]) 

    fuel_sources = {
    "Coal": FuelSources("Coal", .760, False, 24, 24, 160),
    "Gas": FuelSources("Gas", .370, False, 0, 0, 120),
    "Oil": FuelSources("Oil", .406, False, 1, 1, 100),
    "Uranium": FuelSources("Uranium", 0, False, 48, 240, 10),
    "Solar": FuelSources("Solar", 0, False, 0, 0, 5),
    "Wind": FuelSources("Wind", 0, False, 0, 0, 5),
    "Hydro": FuelSources("Hydro", 0, False, 0, 0, 5),
    "Biomass": FuelSources("Biomass", 0, False, 12, 12, 10)
    }

    for fuel_source in fuel_sources.values():
        network.add("Carrier", **fuel_source.carrier_characteristics())

    generators = [
    {"name": "GER-Hydro_ROR","bus": "Germany", "carrier": "Hydro", "p_nom": 3933, "p_min_pu": 0, "p_max_pu": 1,
     "marginal_cost": fuel_sources["Hydro"].primary_cost, "efficiency": 1,
     **(fuel_sources["Hydro"].generator_characteristics())},
    {"name": "GER-WindOnshore","bus": "Germany", "carrier": "Wind", "p_nom": 115000, "p_min_pu": 0, "p_max_pu": wind_on_shore[0:time_horizon_in_hours]["value"].values,
     "marginal_cost": fuel_sources["Wind"].primary_cost, "efficiency": 1,
     **(fuel_sources["Wind"].generator_characteristics())},
    {"name": "GER-WindOffshore","bus": "Germany", "carrier": "Wind", "p_nom": 30185, "p_min_pu": 0, "p_max_pu": wind_off_shore[0:time_horizon_in_hours]["value"].values,
     "marginal_cost": fuel_sources["Wind"].primary_cost, "efficiency": 1,
     **(fuel_sources["Wind"].generator_characteristics())},
    {"name": "GER-Solar","bus": "Germany", "carrier": "Solar", "p_nom": 215002, "p_min_pu": 0, "p_max_pu": solar_pv[0:time_horizon_in_hours]["value"].values,
     "marginal_cost": fuel_sources["Solar"].primary_cost, "efficiency": 1,
     **(fuel_sources["Solar"].generator_characteristics())},
    {"name": "GER-Coal","bus": "Germany", "carrier": "Coal", "p_nom": 0, "p_min_pu": 0, "p_max_pu": 1,
     "marginal_cost": fuel_sources["Coal"].primary_cost, "efficiency": 0.40,
     **(fuel_sources["Coal"].generator_characteristics())},
    {"name": "GER-Biomass","bus": "Germany", "carrier": "Biomass", "p_nom": 13067, "p_min_pu": 0, "p_max_pu": 1,
     "marginal_cost": fuel_sources["Biomass"].primary_cost, "efficiency": 0.3999,
     **(fuel_sources["Biomass"].generator_characteristics())},
     {"name": "GER-CCGT","bus": "Germany", "carrier": "Gas", "p_nom": 35504, "p_min_pu": 0, "p_max_pu": 1,
     "marginal_cost": fuel_sources["Gas"].primary_cost, "efficiency": 0.60,
     **(fuel_sources["Gas"].generator_characteristics())},
    {"name": "GER-Oil","bus": "Germany", "carrier": "Oil", "p_nom": 1885, "p_min_pu": 0, "p_max_pu": 1,
     "marginal_cost": fuel_sources["Oil"].primary_cost, "efficiency": 0.45,
     **(fuel_sources["Oil"].generator_characteristics())},
         {"name": "GER-Failure","bus": "Germany", "carrier": "Failure", "p_nom": 1000000, "p_min_pu": 0, "p_max_pu": 1,
     "marginal_cost": 1000, "efficiency": 0.45,
     **(fuel_sources["Gas"].generator_characteristics())},
]

    
    storage_units = [
        {"name": "GER-PumpedHydroOL", "bus": "Germany", "carrier": "Hydro", "p_nom": 2144.10, "p_min_pu": -0.8680, "p_max_pu": 1,
    "max_hours": 204, "efficiency_store": 0.93, "efficiency_dispatch": 1, "state_of_charge_initial": 200000},
        {"name": "GER-PumpedHydroCL", "bus": "Germany", "carrier": "Hydro", "p_nom": 7009.84, "p_min_pu": -1.0224, "p_max_pu": 1,
    "max_hours": 39.39, "efficiency_store": 0.93, "efficiency_dispatch": 1, "state_of_charge_initial": 150000},
        {"name": "Battery", "bus": "Germany", "p_nom": 3200.40, "p_min_pu": -1, "p_max_pu": 1,
    "max_hours": 17.79, "efficiency_store": 0.90, "efficiency_dispatch": 0.90, "state_of_charge_initial":30000},
    ]
    
    for generator in generators:
        network.add("Generator", **generator, )
    

    for storage_unit in storage_units:
        network.add("StorageUnit", **storage_unit, )


    loads = [
    {"name": "Germany-load", "bus": "Germany", "carrier": "AC", "p_set": demand[0:time_horizon_in_hours]["value"].values},
    ]   
    
    for load in loads:
        network.add("Load", **load)
        
        
def add_iberian(network: pypsa.Network(), climatic_year: int, time_horizon_in_hours: int):
    country = "iberian"
    full_demand = pd.read_csv("./data/demand_2030_Iberian.csv", sep=";", index_col=1, parse_dates=True).groupby(pd.Grouper(key="climatic_year"))
    full_wind_on_shore = pd.read_csv("./data/capa_factor_2030_Iberian_onshore.csv", sep=";", index_col=1, parse_dates=True).groupby(pd.Grouper(key="climatic_year"))
    full_wind_off_shore = pd.read_csv("./data/capa_factor_2030_Iberian_offshore.csv", sep=";", index_col=1, parse_dates=True).groupby(pd.Grouper(key="climatic_year"))
    full_solar = pd.read_csv("./data/capa_factor_2030_Iberian_solar.csv", sep=";", index_col=1, parse_dates=True).groupby(pd.Grouper(key="climatic_year"))


    

    demand = full_demand.get_group(climatic_year)
    solar = full_solar.get_group(climatic_year)
    wind_on_shore = full_wind_on_shore.get_group(climatic_year)
    wind_off_shore = full_wind_off_shore.get_group(climatic_year)
    
    network.snapshots = demand.index[0:time_horizon_in_hours]
    
    network.add("Bus", name="Iberian_Peninsula", x=-3.7037902, y=40.4168)
    
    coal_marginal_costs = 160
    gas_marginal_costs = 120
    oil_marginal_costs = 100
    nuclear_marginal_costs = 40
    hydro_marginal_costs = 2
    wind_marginal_costs = 1
    solar_marginal_costs = 3
    biomass_marginal_costs = 10


    reservoir_max_hours = 1058
    pumped_max_hours = 590
    battery_max_hours = 2
    H2_max_hours = 0
    
    generators = [
    {"name": f"{country}-OCGT", "carrier": "Gas", "p_nom": 2139, "p_min_pu": 0, "p_max_pu": 1, "marginal_cost": gas_marginal_costs, "efficiency": 0.4,
     "committable": False, "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}BioEnergies", "carrier": "BioEnergies", "p_nom":0, "p_min_pu": 0, "p_max_pu": 1, "marginal_cost": biomass_marginal_costs, "efficiency": 0.5, 
     "committable": False, "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Hydroelectric", "carrier":"Hydro", "p_nom": 4196, "p_min_pu": 0, "p_max_pu": 1, "marginal_cost": hydro_marginal_costs, "efficiency": 1, "committable": False,
     "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Wind_on_shore", "carrier": "Wind_on_shore", "p_nom": 57017, "p_min_pu": 0, "p_max_pu": wind_on_shore.value.to_numpy(), "marginal_cost": wind_marginal_costs, "efficiency":1, "committable": False,
     "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Wind_off_shore", "carrier": "Wind_off_shore", "p_nom": 3046, "p_min_pu": 0, "p_max_pu": wind_off_shore.value.to_numpy(), "marginal_cost": wind_marginal_costs, "efficiency":1, "committable": False,
     "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Nuclear", "carrier": "Nuclear", "p_nom": 5100, "p_min_pu":0, "p_max_pu": 1, "marginal_cost": nuclear_marginal_costs, "efficiency":1, "committable": False,
     "min_up_time": 24, "min_down_time": 24},
    {"name": f"{country}Solar", "carrier": "Solar", "p_nom": 80606, "p_min_pu": 0, "p_max_pu": solar.value.to_numpy(), "marginal_cost": solar_marginal_costs, "efficiency":1, "committable": False,
     "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Failure", "carrier": "Failure", "p_nom": 100000, "p_min_pu":0, "p_max_pu": 1, "marginal_cost": 1000, "efficiency":1, "committable": False,
     "min_up_time": 1, "min_down_time": 1}
]
    
    storage_units = [
        {"name": f"{country}Reservoir", "carrier": "Reservoir", "p_nom": 15180, "p_min_pu": 0, "p_max_pu": 1, "max_hours": reservoir_max_hours, "efficiency": 1, "cyclic_state_of_charge": True, "p_nom_discharge" : 100, "p_nom_charge" : 100},
        {"name": f"{country}Pumped", "carrier": "Pumped", "p_nom": 13367, "p_min_pu": 0, "p_max_pu": 1, "max_hours": pumped_max_hours, "efficiency": 1, "cyclic_state_of_charge": True, "p_nom_discharge" : 100, "p_nom_charge" : 100},
        {"name": f"{country}Battery", "carrier": "Battery", "p_nom": 5000, "p_min_pu": 0, "p_max_pu": 1, "max_hours": battery_max_hours, "efficiency": 1, "cyclic_state_of_charge": True, "p_nom_discharge" : 100, "p_nom_charge" : 100},
        {"name": f"{country}H2", "carrier": "H2", "p_nom": 0, "p_min_pu": 0, "p_max_pu": 1, "max_hours": H2_max_hours, "efficiency": 1, "cyclic_state_of_charge": True, "p_nom_discharge" :100, "p_nom_charge" : 100},
]
    
    for generator in generators:
        network.add("Generator", bus="Iberian_Peninsula", **generator,)
    

    for storage in storage_units:
        network.add("Store", bus="Iberian_Peninsula", **storage,)


    loads = [
    {"name": "Iberian_Peninsula-load", "bus": "Iberian_Peninsula", "carrier": "AC","p_set": demand[0:time_horizon_in_hours]["value"].values*1},
    {"name": f"{country}Curtailment-load", "bus": "Curtailment", "carrier": "AC","p_set": 10000},
]
    
    for load in loads:
        network.add("Load", **load)
        
        

def add_poland(network: pypsa.Network(), climatic_year: int, time_horizon_in_hours: int, country: str = "poland", year: int = 2030, x: float = 19.397666, y: float = 52.455567):
    country = "poland"
    full_demand = pd.read_csv(f"./data/demand_{year}_{country}.csv", sep=";", index_col=1, parse_dates=True).groupby(pd.Grouper(key="climatic_year"))
    full_wind_on_shore = pd.read_csv(f"./data/capa_factor_{year}_{country}_onshore.csv", index_col=1, parse_dates=True, sep=";").groupby(pd.Grouper(key="climatic_year"))
    full_solar = pd.read_csv(f"./data/capa_factor_{year}_{country}_solar.csv", index_col=1, parse_dates=True, sep=";").groupby(pd.Grouper(key="climatic_year"))
    full_wind_off_shore = pd.read_csv(f"./data/capa_factor_{year}_{country}_offshore.csv", index_col=1, parse_dates=True, sep=";").groupby(pd.Grouper(key="climatic_year"))

    

    demand = full_demand.get_group(climatic_year)
    solar = full_solar.get_group(climatic_year)
    wind_on_shore = full_wind_on_shore.get_group(climatic_year)
    wind_off_shore = full_wind_off_shore.get_group(climatic_year)
    
    network.snapshots = demand.index[0:time_horizon_in_hours]
    network.add("Bus", name=country, x = x, y = y)

    #Marginal cost & CO2 emission for each carrier
    cost_of_CO2 = 100
    #In eur / MWh, marginal costs
    carriers_marg = dict(
        Battery = 0,
        Biofuel = 0,
        Coal = 80,
        Gas = 120,
        Oil = 100,
        Hydrogen = 0,
        Hydro = 2,
        Nuclear = 40,
        Pumped = 0,
        Reservoir = 0,
        Solar = 3,
        Wind = 1,
        Failure = 1000,
        Lignite = 70,
        Others_non_renewable = 100,
        Others_renewable = 0,
        Batteries = 0,
    )
    #In t / MWh
    #kd
    carriers_CO2 = dict(
        Battery = 0,
        Biofuel = 0,
        Coal = 0.760,
        Gas = 0.370,
        Oil = 0.406,
        Hydrogen = 0,
        Hydro = 0,
        Nuclear = 0,
        Pumped = 0,
        Reservoir = 0,
        Solar = 0,
        Wind = 0,
        Failure = 0,
        Lignite = 0.800,
        Others_non_renewable = 0.400,
        Others_renewable = 0,
        Batteries = 0,
    )

    for key, value in carriers_CO2.items():
        try:
            network.add("Carrier", key, co2_emissions=value)
        except:
            pass

    carriers = dict()
    for key in carriers_CO2.keys():
        carriers[key] = carriers_marg[key] + cost_of_CO2 * carriers_CO2[key] / 1000

    #Min up & dowm time in hours. If not specified, it is 1
    carriers_min_up_down = dict(
        Nuclear = (24, 24),
        Coal = (5, 5),
        Lignite = (5, 5),
    )

    #Add generators and storage units
    capacities = pd.read_csv(f"data/ERAA_National_Estimates_capacities_{year}_{country}.csv", sep=";", index_col=0)

    capacity = "power_capacity (MW)"
    ene_capacity = "energy_capacity (MWh)"

    for index, row in capacities.iterrows():
        if row[capacity] > 0 and np.isnan(row[ene_capacity]):
            name = index
            carrier = name.split(" ")[0]
            if name == "Hard Coal":
                name = "Coal"
                carrier ="Coal"
            if name == "Others non-renewable":
                carrier = "Others_non_renewable"
            elif name == "Others renewable":
                carrier = "Others_renewable"
            marg_cost = carriers[carrier]
            min_up, min_down = carriers_min_up_down.get(carrier, (1, 1))
            comm = False
            min_pu = 0

            network.add("Generator", country + "_" + name, bus=country, carrier=carrier, p_nom=row[capacity], marginal_cost=marg_cost, min_up_time=min_up, min_down_time=min_down, p_min_pu = min_pu, committable=comm)
        elif row[capacity] > 0 and not np.isnan(row[ene_capacity]):
            name = index
            carrier = name.split(" ")[0]
            marg_cost = carriers[carrier]
            max_hours = row[ene_capacity] / row[capacity]
            min_up, min_down = carriers_min_up_down.get(carrier, (1, 1))
            comm = True
            network.add("StorageUnit", country + "_" + name, bus=country, carrier=carrier, p_nom=row[capacity], marginal_cost=marg_cost, max_hours=max_hours, p_min_pu = -1, p_max_pu = 1)

    try:
        network.add("Generator", f"{country}Failure", bus=country, carrier="Failure", p_nom=100000, marginal_cost=100000 , min_up_time=1, min_down_time=1, committable=False)
    except:
        pass

    loads = [
    {"name": f"{country}-load", "bus": country , "carrier": "AC","p_set": demand[0:time_horizon_in_hours]["value"].values*1},
    {"name": f"{country}Curtailment-load", "bus": "Curtailment", "carrier": "AC","p_set": 10000},
    ]
        
    for load in loads:
        network.add("Load", **load)

    network.generators_t.p_max_pu[f"{country}_Solar (Photovoltaic)"] = solar["value"][0:time_horizon_in_hours].values
    network.generators_t.p_max_pu[f"{country}_Wind Onshore"] = wind_on_shore["value"][0:time_horizon_in_hours].values
    network.generators_t.p_max_pu[f"{country}_Wind Offshore"] = wind_off_shore["value"][0:time_horizon_in_hours].values



def add_france(network: pypsa.Network(), climatic_year: int, time_horizon_in_hours: int):
    country = "France"
    full_demand = pd.read_csv("./data/demand_2030_France.csv", sep=";", index_col=1, parse_dates=True).groupby(pd.Grouper(key="climatic_year"))
    full_wind_on_shore = pd.read_csv("./data/capa_factor_2030_France_onshore.csv", index_col=1, parse_dates=True, sep=";").groupby(pd.Grouper(key="climatic_year"))
    full_solar = pd.read_csv("./data/capa_factor_2030_France_solar.csv", index_col=1, parse_dates=True, sep=";").groupby(pd.Grouper(key="climatic_year"))
    full_wind_off_shore = pd.read_csv("./data/capa_factor_2030_France_offshore.csv", index_col=1, parse_dates=True, sep=";").groupby(pd.Grouper(key="climatic_year"))
    full_reservoir = pd.read_csv("./data/ENTSOE_calculated_inflows_FR.csv")
    
    reservoir_production_raw = full_reservoir[full_reservoir["datetime_UTC"].astype(str).str.startswith("2018")]
    reservoir_production = reservoir_production_raw.reindex(reservoir_production_raw.index.repeat(24*7)).reset_index(drop=True)["inflows_MW"][:365*24]

    demand = full_demand.get_group(climatic_year)
    solar = full_solar.get_group(climatic_year)
    wind_on_shore = full_wind_on_shore.get_group(climatic_year)
    wind_off_shore = full_wind_off_shore.get_group(climatic_year)
    
    network.snapshots = demand.index[0:time_horizon_in_hours]
    
    network.add("Bus", name="France", x=2.33333, y=48.86667)
    
    gas_marginal_costs = 120
    nuclear_marginal_costs = 40
    hydro_marginal_costs = 2
    wind_marginal_costs = 1
    solar_marginal_costs = 3
    biomass_marginal_costs = 10


    reservoir_max_hours = 321
    pumped_max_hours = 30
    battery_max_hours = 6
    
    generators = [
    {"name": f"{country}Nuclear", "carrier": "Nuclear", "p_nom": 59400, "p_min_pu": 0.3, "p_max_pu": 1, "marginal_cost": nuclear_marginal_costs, "efficiency": 0.33,
     "committable": False, "min_up_time": 24, "min_down_time": 24},
    {"name": f"{country}WindOnshore", "carrier": "Wind", "p_nom":11000, "p_min_pu": 0, "p_max_pu": wind_on_shore.value, "marginal_cost": wind_marginal_costs, "efficiency": 0.4, 
     "committable": False, "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}WindOffshore", "carrier":"Wind", "p_nom": 5800, "p_min_pu": 0, "p_max_pu": wind_off_shore.value, "marginal_cost": wind_marginal_costs, "efficiency": 0.5, "committable": False,
     "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Solar", "carrier": "Solar", "p_nom": 47300, "p_min_pu": 0, "p_max_pu": solar.value, "marginal_cost": solar_marginal_costs, "efficiency": 0.12, "committable": False,
     "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}OCGT", "carrier": "H2", "p_nom": 6700, "p_min_pu": 0, "p_max_pu": 1, "marginal_cost": gas_marginal_costs, "efficiency": 0.5, "committable": False,
     "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}BioEnergies", "carrier": "BioEnergies", "p_nom": 2300, "p_min_pu":0, "p_max_pu": 1, "marginal_cost": biomass_marginal_costs, "efficiency": 0.3, "committable": False,
     "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Hydro", "carrier": "Hydro", "p_nom": 26900, "p_min_pu": 0, "p_max_pu": 1, "marginal_cost": hydro_marginal_costs, "efficiency": 0.9, "committable": False,
     "min_up_time": 1, "min_down_time": 1},
    {"name": f"{country}Failure", "carrier": "Failure", "p_nom": 100000, "p_min_pu":0, "p_max_pu": 1, "marginal_cost": 1000, "efficiency":1, "committable": False,
     "min_up_time": 1, "min_down_time": 1}
]

    storage_units = [
        {"name": f"{country}Reservoir", "carrier": "Reservoir", "p_nom": 10100, "p_min_pu": reservoir_production, "p_max_pu": 1, "max_hours": reservoir_max_hours, "efficiency": 1, "cyclic_state_of_charge": True, "p_nom_discharge" : 100, "p_nom_charge" : 100},
        {"name": f"{country}Pumped", "carrier": "Pumped", "p_nom": 8500, "p_min_pu": -1, "p_max_pu": 1, "max_hours": pumped_max_hours, "efficiency": 1, "cyclic_state_of_charge": True, "p_nom_discharge" : 100, "p_nom_charge" : 100},
        {"name": f"{country}Battery", "carrier": "Battery", "p_nom": 2100, "p_min_pu": -1, "p_max_pu": 1, "max_hours": battery_max_hours, "efficiency": 1, "cyclic_state_of_charge": True, "p_nom_discharge" : 100, "p_nom_charge" : 100},
]
    
    for generator in generators:
        network.add("Generator", bus="France", **generator,)
    

    for storage in storage_units:
        network.add("Store", bus="France", **storage,)


    loads = [
    {"name": "France-load", "bus": "France", "carrier": "AC","p_set": demand[0:time_horizon_in_hours]["value"].values*1},
    {"name": f"{country}Curtailment-load", "bus": "Curtailment", "carrier": "AC","p_set": 10000},
]
    
    for load in loads:
        network.add("Load", **load)
        
        
        