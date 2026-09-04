"""
Deterministic Physical Downscaling Configuration
Strict Provenance Rule: Every numeric constant must have a source cited here.
"""

# Domain Settings
DOMAIN = {
    "lat_min": 13.0,
    "lat_max": 17.5,
    "lon_min": 73.5,
    "lon_max": 76.5
}

# -------------------------------------------------------------------------
# Temperature Physical Constants
# -------------------------------------------------------------------------
# Environmental Lapse Rate [°C/km or K/km]
# Source: International Civil Aviation Organization (ICAO) Standard Atmosphere (1993)
# Note: This is an average. Local empirical fits (4.5 to 7.5) will be swept during validation.
LAPSE_RATE_DEFAULT = 6.5

# -------------------------------------------------------------------------
# Humidity Physical Constants (Magnus-Tetens Formula)
# -------------------------------------------------------------------------
# Saturation Vapor Pressure constants over water
# Equation: e_s = a * exp((b * T) / (T + c)) where T is in °C
# Source: Alduchov, O. A., & Eskridge, R. E. (1996). 
# Improved Magnus Form Approximation of Saturation Vapor Pressure.
# Journal of Applied Meteorology, 35(4), 601-609.
MAGNUS_A = 0.61094  # [kPa]
MAGNUS_B = 17.625   # [dimensionless]
MAGNUS_C = 243.04   # [°C]

# Barometric Formula Constants
# Source: Standard Atmosphere (1976), NOAA/NASA/USAF
GRAVITY = 9.80665              # [m/s^2] Standard gravity
MOLAR_MASS_AIR = 0.0289644     # [kg/mol] Molar mass of Earth's air
UNIVERSAL_GAS_CONST = 8.3144598 # [J/(mol·K)] Universal gas constant

# -------------------------------------------------------------------------
# Wind Downscaling Constants
# -------------------------------------------------------------------------
# Topographic Exposure Factor bounds
# Used to scale 10m wind speed based on local relief.
# Source: ESTIMATED — NO SOURCE (placeholder for unvalidated topographic exposure index logic)
WIND_EXPOSURE_MIN = 0.5   # Maximum sheltering deceleration (valley bottoms)
WIND_EXPOSURE_MAX = 1.5   # Maximum exposure acceleration (ridge crests)

# -------------------------------------------------------------------------
# Agronomic Constants (FAO-56 Penman-Monteith)
# -------------------------------------------------------------------------
# Source: Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. (1998). 
# Crop evapotranspiration - Guidelines for computing crop water requirements - FAO Irrigation and drainage paper 56.

# Psychrometric constant [kPa/°C] at sea level 
# (Will be adjusted by elevation via barometric pressure internally)
# Source: FAO-56 Equation 8
PSYCHROMETRIC_CONST_BASE = 0.0666

# Hargreaves-Samani empirical coefficient (Fallback when radiation is unavailable)
# Source: Hargreaves, G. H., & Samani, Z. A. (1985). Reference crop evapotranspiration from temperature.
HARGREAVES_COEFF = 0.0023

# Albedo (Reflectance) for the reference grass crop
# Source: FAO-56 (Section: Reference Crop)
ALBEDO_GRASS = 0.23

# Stefan-Boltzmann Constant [MJ / (K^4 m^2 day)]
# Source: FAO-56 Equation 39
STEFAN_BOLTZMANN_MJ_DAY = 4.903e-9

# -------------------------------------------------------------------------
# Advisory Thresholds (Agronomic Flags)
# -------------------------------------------------------------------------
# Spray-suitability maximum wind speed [m/s]
# Source: UK Code of Practice for Using Plant Protection Products (DEFRA, 2006). 
# Optimal is 1-2 m/s, risky above 3.2 m/s, strictly unsuitable above 5.5 m/s.
SPRAY_MAX_WIND = 3.2

# Leaf-wetness / Disease Risk RH threshold [%]
# Source: Sentelhas, P. C. et al. (2008). Leaf wetness duration measurement and estimation. 
# RH > 90% is commonly used as a proxy for leaf wetness onset.
DISEASE_RH_THRESHOLD = 90.0

# Heat stress threshold for generic cereal [°C]
# Source: Hatfield, J. L., & Prueger, J. H. (2015). Temperature extremes: Effect on plant growth and development.
HEAT_STRESS_THRESHOLD = 35.0
