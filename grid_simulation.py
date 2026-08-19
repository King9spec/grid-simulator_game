"""
Étape 1 : Moteur de simulation de réseau électrique (fondation SCADA)
======================================================================

Un seul rôle par fonction :
  - build_network()   -> construit la topologie (2 nœuds, 1 ligne)
  - solve_power_flow() -> résout l'écoulement de puissance
  - export_scada_data() -> transforme les résultats en JSON "façon SCADA"

Aucune valeur par défaut cachée, aucun fallback : si le power flow ne
converge pas, pandapower lève une exception (LoadflowNotConverged) et le
script s'arrête. C'est voulu : une non-convergence EST une donnée
intéressante pour le futur module de crise (ex: réseau qui s'effondre).
"""

import json
import pandapower as pp

# ----------------------------------------------------------------------
# ZONE DE JEU : modifie ces valeurs pour tester différents scénarios
# ----------------------------------------------------------------------
CITY_LOAD_MW = 8.0          # Puissance active consommée par la ville
CITY_LOAD_MVAR = 2.0        # Puissance réactive consommée par la ville
LINE_LENGTH_KM = 10.0       # Longueur de la ligne de transmission
LINE_STD_TYPE = "NAYY 4x50 SE"  # Type standard de ligne (capacité, impédance)
SLACK_VOLTAGE_PU = 1.02     # Tension de consigne à la centrale (en p.u.)


def build_network() -> pp.pandapowerNet:
    """Construit le réseau minimal : 1 générateur, 1 ligne, 1 charge."""
    net = pp.create_empty_network(name="mvp_grid")

    bus_plant = pp.create_bus(net, vn_kv=20.0, name="Centrale (Slack)")
    bus_city = pp.create_bus(net, vn_kv=20.0, name="Ville (Charge)")

    pp.create_ext_grid(
        net, bus=bus_plant, vm_pu=SLACK_VOLTAGE_PU, name="Centrale principale"
    )

    pp.create_line(
        net,
        from_bus=bus_plant,
        to_bus=bus_city,
        length_km=LINE_LENGTH_KM,
        std_type=LINE_STD_TYPE,
        name="Ligne Centrale-Ville",
    )

    pp.create_load(
        net,
        bus=bus_city,
        p_mw=CITY_LOAD_MW,
        q_mvar=CITY_LOAD_MVAR,
        name="Consommation Ville",
    )

    return net


def solve_power_flow(net: pp.pandapowerNet) -> None:
    """Résout l'écoulement de puissance. Lève une exception si ça diverge."""
    pp.runpp(net)


def export_scada_data(net: pp.pandapowerNet) -> dict:
    """Extrait les résultats critiques sous forme de dict façon flux SCADA."""
    line = net.res_line.iloc[0]
    bus_city_voltage = net.res_bus.loc[net.load.at[0, "bus"], "vm_pu"]
    ext_grid = net.res_ext_grid.iloc[0]

    return {
        "line": {
            "loading_percent": round(float(line["loading_percent"]), 2),
            "p_from_mw": round(float(line["p_from_mw"]), 3),
            "q_from_mvar": round(float(line["q_from_mvar"]), 3),
        },
        "city_bus": {
            "voltage_pu": round(float(bus_city_voltage), 4),
        },
        "plant_injection": {
            "p_mw": round(float(ext_grid["p_mw"]), 3),
            "q_mvar": round(float(ext_grid["q_mvar"]), 3),
        },
    }


if __name__ == "__main__":
    net = build_network()
    solve_power_flow(net)
    scada_payload = export_scada_data(net)
    print(json.dumps(scada_payload, indent=2, ensure_ascii=False))