import numpy as np
import itertools
from engine.deterministic import temperature, humidity, wind, agronomic

def test_ranges():
    print("=" * 60)
    print("PHYSICS PURE FUNCTION RANGE TESTING (NOT VALIDATION)")
    print("=" * 60)
    
    # Define realistic ranges
    temps_c = np.linspace(5.0, 45.0, 10)
    dewpoints_c = np.linspace(-5.0, 44.0, 10)
    elevs_m = np.linspace(0.0, 1500.0, 5)
    winds_ms = np.linspace(0.0, 20.0, 5)
    rad_mj = np.linspace(5.0, 30.0, 5)
    
    # 1. Temperature Range Test
    print("\n--- Temperature Range Test ---")
    temps_k = temps_c + 273.15
    for (t_coarse, e_coarse, e_fine) in itertools.product(temps_k, elevs_m, elevs_m):
        t_out = temperature.downscale_temperature(
            np.array([t_coarse]), 
            np.array([e_coarse]), 
            np.array([e_fine])
        )[0]
        
        if np.isnan(t_out) or np.isinf(t_out):
            print(f"FAILED: Output is NaN/Inf. T_coarse={t_coarse}, E_c={e_coarse}, E_f={e_fine}")
        if t_out < 200.0 or t_out > 330.0:
            print(f"FAILED: Implausible temperature output. T_out={t_out}")
            
    print("Temperature range test complete (checked for NaN/Inf/implausible).")

    # 2. Humidity Range Test
    print("\n--- Humidity Range Test ---")
    for (t_coarse, d_coarse, t_fine, e_coarse, e_fine) in itertools.product(temps_k, dewpoints_c + 273.15, temps_k, elevs_m, elevs_m):
        if d_coarse > t_coarse:
            continue # Skip unphysical dewpoint > temp
            
        p_coarse = np.array([101325.0])
        rh_out = humidity.downscale_humidity(
            np.array([t_coarse]), 
            np.array([d_coarse]), 
            p_coarse, 
            np.array([t_fine]), 
            np.array([e_coarse]), 
            np.array([e_fine])
        )[0]
        
        if np.isnan(rh_out) or np.isinf(rh_out):
            print(f"FAILED: RH output is NaN/Inf. T_coarse={t_coarse}, D_c={d_coarse}, T_fine={t_fine}")
        if rh_out < 0.0 or rh_out > 100.0:
            # We expect clamping, but the function clamps internally and warns. 
            # If it escapes clamping, it's a failure.
            print(f"FAILED: RH clamping failed. RH_out={rh_out}")
            
    print("Humidity range test complete (checked for NaN/Inf/implausible). Note: Clamping is handled internally and logged.")

    # 3. Wind Range Test
    print("\n--- Wind Range Test ---")
    for (w, e_coarse, e_fine) in itertools.product(winds_ms, elevs_m, elevs_m):
        # We model exposure index roughly from -1 to 1
        exposure = np.array([0.5]) 
        u_out, v_out = wind.downscale_wind(np.array([w]), np.array([0.0]), exposure)
        if np.isnan(u_out[0]) or np.isinf(u_out[0]):
            print("FAILED: Wind output is NaN/Inf.")
    print("Wind range test complete (checked for NaN/Inf).")

    # 4. ETo Range Test
    print("\n--- Agronomic ETo Range Test ---")
    for (t_mean, t_diff, ra) in itertools.product(temps_c, np.linspace(1.0, 15.0, 5), rad_mj):
        t_max = np.array([t_mean + t_diff/2])
        t_min = np.array([t_mean - t_diff/2])
        eto = agronomic.calc_eto_hargreaves(t_min, t_max, np.array([t_mean]), np.array([ra]))[0]
        
        if np.isnan(eto) or np.isinf(eto):
            print(f"FAILED: ETo output is NaN/Inf.")
        if eto < 0.0 or eto > 20.0: # 20mm/day is physically extremely high, anything over is implausible
            print(f"FAILED: Implausible ETo output. ETo={eto} mm/day")
    print("Agronomic ETo range test complete (checked for NaN/Inf/implausible).")
    
    print("\n============================================================")
    print("ALL RANGE TESTS FINISHED.")
    print("============================================================")

if __name__ == "__main__":
    test_ranges()
