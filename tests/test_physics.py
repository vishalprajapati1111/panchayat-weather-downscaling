import pytest
import numpy as np
from engine.deterministic import temperature, humidity, wind, agronomic

def test_temperature_anchored():
    # Externally anchored test: A 1000m rise at standard lapse rate (6.5 K/km) 
    # produces exactly 6.5 K of cooling. Explicitly check the sign convention.
    t_input_k = np.array([300.0])
    elev_coarse = np.array([0.0])
    elev_fine = np.array([1000.0])
    
    t_out_k = temperature.downscale_temperature(t_input_k, elev_coarse, elev_fine, lapse_rate=6.5)
    
    # Sign check: higher elevation -> MUST be colder
    assert t_out_k[0] < t_input_k[0], "Higher elevation must result in lower temperature"
    np.testing.assert_almost_equal(t_out_k[0], 293.5)

def test_temperature_inversion():
    # Sign convention test: A 500m drop produces warming.
    t_input_k = np.array([300.0])
    elev_coarse = np.array([1000.0])
    elev_fine = np.array([500.0])
    
    t_out_k = temperature.downscale_temperature(t_input_k, elev_coarse, elev_fine, lapse_rate=6.5)
    
    # Lower elevation -> MUST be warmer
    assert t_out_k[0] > t_input_k[0]
    np.testing.assert_almost_equal(t_out_k[0], 303.25)

def test_magnus_anchored():
    # Externally anchored test: FAO-56 Table 3 Saturation Vapour Pressure
    # T = 0.0 C -> es = 0.611 kPa
    # T = 20.0 C -> es = 2.339 kPa
    es_0 = humidity.calc_es_magnus(np.array([0.0]))
    es_20 = humidity.calc_es_magnus(np.array([20.0]))
    
    np.testing.assert_almost_equal(es_0[0], 0.611, decimal=3)
    np.testing.assert_almost_equal(es_20[0], 2.339, decimal=2)

def test_humidity_monotonicity():
    # Monotonicity test: Cooling air at constant dewpoint MUST raise RH.
    coarse_temp_k = np.array([300.15]) 
    coarse_dewpoint_k = np.array([283.15]) 
    coarse_pressure_pa = np.array([101325.0])
    
    # Cool by 5 degrees, pressure constant
    t_fine_cooler_k = np.array([295.15])
    
    # Heat by 5 degrees, pressure constant
    t_fine_hotter_k = np.array([305.15])
    
    elev = np.array([100.0])
    
    rh_base = humidity.downscale_humidity(coarse_temp_k, coarse_dewpoint_k, coarse_pressure_pa, coarse_temp_k, elev, elev)[0]
    rh_cooler = humidity.downscale_humidity(coarse_temp_k, coarse_dewpoint_k, coarse_pressure_pa, t_fine_cooler_k, elev, elev)[0]
    rh_hotter = humidity.downscale_humidity(coarse_temp_k, coarse_dewpoint_k, coarse_pressure_pa, t_fine_hotter_k, elev, elev)[0]
    
    assert rh_cooler > rh_base, "Cooling air at constant dewpoint must raise relative humidity"
    assert rh_hotter < rh_base, "Warming air at constant dewpoint must lower relative humidity"
    assert rh_cooler <= 100.0, "Relative humidity cannot exceed 100%"

def test_eto_anchored():
    # Externally anchored test: FAO-56 Chapter 4 (Example 19)
    # Tmax = 26.6 C, Tmin = 14.8 C, Tmean = 20.7 C
    # Extraterrestrial Radiation Ra = 40.6 MJ/m2/day
    # Expected ETo = ~5.0 mm/day
    eto = agronomic.calc_eto_hargreaves(
        t_min=np.array([14.8]),
        t_max=np.array([26.6]),
        t_mean=np.array([20.7]),
        ra_mj_m2_day=np.array([40.6])
    )
    # Result is roughly 5.0 mm/day. Tolerance of 0.1 mm/day.
    assert np.abs(eto[0] - 5.0) < 0.1

def test_unit_guards():
    # Ensure functions raise ValueError when passing Kelvin into Celsius functions and vice-versa
    
    # 1. Temperature downscale expects Kelvin, passing Celsius should fail
    with pytest.raises(ValueError, match="appears to be in Celsius"):
        temperature.downscale_temperature(
            coarse_temp=np.array([25.0]), # Celsius
            coarse_elev=np.array([0.0]),
            fine_elev=np.array([100.0])
        )
        
    # 2. Humidity calc_es_magnus expects Celsius, passing Kelvin should fail
    with pytest.raises(ValueError, match="calc_es_magnus expects Celsius"):
        humidity.calc_es_magnus(np.array([300.0]))
        
    # 3. Humidity downscale expects Kelvin, passing Celsius should fail
    with pytest.raises(ValueError, match="downscale_humidity expects Kelvin"):
        humidity.downscale_humidity(
            np.array([25.0]), np.array([288.15]), np.array([100000.0]), 
            np.array([283.15]), np.array([100.0]), np.array([100.0])
        )
        
    # 4. ETo Hargreaves expects Celsius, passing Kelvin should fail
    with pytest.raises(ValueError, match="calc_eto_hargreaves expects Celsius"):
        agronomic.calc_eto_hargreaves(
            t_min=np.array([285.0]), # Kelvin
            t_max=np.array([295.0]),
            t_mean=np.array([290.0]),
            ra_mj_m2_day=np.array([20.0])
        )
