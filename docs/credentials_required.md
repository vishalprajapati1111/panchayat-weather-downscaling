# IMERG Credential Requirements

Accessing the GPM IMERG V07 precipitation dataset requires provisioning credentials for either Google Earth Engine (GEE) or NASA Earthdata. This is a one-time setup on this machine.

## Option 1: Google Earth Engine (Recommended)

Google Earth Engine provides direct, subsetted extraction of IMERG data without downloading massive global files. It appears to be installed on your machine but requires interactive authentication.

### Steps to unblock:
1. Open your terminal in this workspace.
2. Run the command: `earthengine authenticate`
3. A browser window will open automatically (to `accounts.google.com`).
4. Select the Google account you wish to use (you must have a registered Cloud project, the free non-commercial tier is sufficient).
5. Follow the prompts to grant the necessary permissions. The browser will redirect to `localhost:8085` to hand off the token back to your terminal.
6. Once complete, the terminal will indicate successful authentication.

**Note for headless environments:** If a browser window did not pop up (or cannot be reached), cancel the command and run `earthengine authenticate --auth_mode=notebook` instead, which will provide a URL to copy/paste and an authorization code to enter manually.

**Estimated time:** 3-5 minutes.

## Option 2: NASA Earthdata (Fallback)

If you prefer not to use GEE, the data can be fetched directly from NASA's GES DISC server. This requires a free Earthdata account.

### Steps to unblock:
1. Register for an account at [urs.earthdata.nasa.gov](https://urs.earthdata.nasa.gov/).
2. Create a `.netrc` file in your home directory (`C:\Users\VISHAL\.netrc`) with the following content:
   ```text
   machine urs.earthdata.nasa.gov
   login YOUR_EARTHDATA_USERNAME
   password YOUR_EARTHDATA_PASSWORD
   ```
3. Ensure the script is configured to use the Earthdata fallback path for `GPM_3IMERGDF`.

**Estimated time:** 5-10 minutes.

---
*Once either option is provisioned, the disagreement field between CHIRPS and IMERG (required for Step 4 weight uncertainty bounds) can be successfully computed.*
