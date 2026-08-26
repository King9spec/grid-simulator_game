Grid simulator Game

Pour l'instant je valide la physique du reseau

reseau|ext     ligne         charge 
 _______                     _______
#_______#--|-------------|--#_______#
          bus           bus 

p_charge = 8_MW
q_charge = 2_MVAR
l_reseau = 10_km
l_type = "NAVY_4X50SE"

r_int_ligne = 6.42_ohm ----->https://www.ttcables.com/wp-content/uploads/2024/05/TDS_NAYY_SE.pdf && https://docs.pypsa.org/v1.0.5/user-guide/components/line-types/
x_int_ligne = 0.83_ohm ----->https://docs.pypsa.org/v1.0.5/user-guide/components/line-types/

Eb = 20_KV
Ep.u(choisi) = 1.02_p.u
Ereel = Eb*Ep.u
Ereel = 20.4_KV


Erxr = (q_charge*r_int_ligne + q_charge*x_int_ligne)/Eb
Erxr = 2647_V

El = Eb-Erxr
El = 17353_V
Ep.u(ligne) = Erxr/Eb
Ep.u(ligne) = 0.867

