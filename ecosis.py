# pip install requests

# This script should be able to query the Ecosis database and extract spectral data
import requests
import urllib.parse
import json
import os

dataset_url = "https://ecosis.org/api/package/search"

# Define query parameters for dataset search (no filters here, just an example search query)
filters = [
    {"Theme":"Dicot"},
    # {"Organization":""},
    # {"Latin Genus":""},
    # {"Latin Species":""},
    # {"Common Name":"northern red oak"},
    # {"Location":""},
]

query_json = json.dumps(filters)
query_encoded = urllib.parse.quote(query_json)
print(query_encoded)

params = {
    'text': 'grass',  # the keyword you want to search for
    'start': 0,       # Pagination start index
    'stop': 6,        # Pagination stop index (fetch 6 results in this example)
    # 'filters': query_encoded  # Example filter: Category = Dicot
}

# Make the GET request to fetch the dataset list
response = requests.get(dataset_url, params=params)

dataset_ids = []
names = []
# Check if the request was successful
if response.status_code == 200:
    datasets = response.json()
    # Print out the number of datasets found
    print(f"Found {datasets['total']} datasets")
    
    # Print out details of the datasets
    for dataset in datasets['items']:
        print(f"Dataset ID: {dataset['_id']}")
        dataset_ids.append(dataset['_id'])
        print(f"Title: {dataset['ecosis']['package_title']}")
        names.append(dataset['ecosis']['package_title'])
        print(f"Organization: {dataset['ecosis']['organization']}")
        print("-----")
else:
    print(f"Error fetching datasets: {response.status_code}")

# spectral_url = "https://ecosis.org/api/package/search?"
# Download results
for idx, data_id in enumerate(dataset_ids):
    spectral_url = f"https://ecosis.org/api/package/{data_id}/export?metadata=false"
    print(spectral_url)
    params = {
        'metadata': False,  # Should the metadata be included in the csv file (boolean)
        # 'filters':, # filters - the array of filters (JSON) (optional)
    }
    
    import pandas as pd
    df = pd.read_csv(spectral_url)
    df = df.apply(pd.to_numeric, errors='coerce')
    wavelengths = df.columns.tolist()
    
    wavelength_num = len(wavelengths)
    # print(wavelength_num)

    spectra = df.iloc[1:].values.tolist()
    # print(f"length of spectra: {len(spectra)}")
    # print(spectra)

    # import numpy as np
    # # Sort, just in case. Though, downloaded data should be in order
    # sorted_indices = np.argsort(wavelengths)
    # sorted_wavelengths = wavelengths[sorted_indices]

    # sorted_spectrum = spectrum[sorted_indices]

    # from scipy.interpolate import interp1d
    # wavelengths = np.linspace(360, 830, 50)
    # f = interp1d(sorted_wavelengths, sorted_spectrum, kind='linear', fill_value='extrapolate')
    # spectrum = f(wavelengths)

    import matplotlib.pyplot as plt
    # plt.plot(wavelengths, spectra[0])
    # plt.xlabel("Wavelengths(nm)")
    # plt.ylabel("Reflectance")
    # # plt.title("Spectra of iterpolated "+spectra_name)
    # # plt.savefig(dir_name + "/" + spectra_name + "-spectra.png")
    # plt.show()

    #Bspline fitting
    import numpy as np
    from scipy.interpolate import splev, splrep
    from sklearn.metrics import mean_squared_error
    import csv

    wavelengths = np.array(wavelengths, dtype=float)

    #### ISOLATE only visible wavelengths/spectrum
    # Create a mask for wavelengths between 380 and 700 (inclusive)
    mask = (wavelengths >= 380) & (wavelengths <= 700)

    # Apply the mask to both wavelengths and spectrum arrays
    filtered_wavelengths = wavelengths[mask]
    # Loop through all the spectra:

    # create dir to hold data for this data:
    dir_name = 'visible-bspline-data'
    os.makedirs(dir_name, exist_ok=True)
    dir_name = dir_name + '/' + names[idx]
    os.makedirs(dir_name, exist_ok=True)

    all_rows = []
    
    all_rows.append(['Number of knots', 'MSE', 'RMSE', 'R2'])  # Column names (header)
    for i in range(0, len(spectra)):
        print(f"Progress {names[idx]}: {str(i / len(spectra))}%", end="\r")
        spectra_dir_name = dir_name + '/' + str(i)
        os.makedirs(spectra_dir_name, exist_ok=True)
        spectrum = np.array(spectra[i], dtype=float)

        filtered_spectrum = spectrum[mask]

        # Experiment with # of knots 
        for num_knots in range(4, 25, 1):
            # Select knot indices, avoid the exact min and max of the wavelengths
            knot_idxs = np.linspace(1, len(filtered_wavelengths) - 2, num_knots, dtype=int)  # Avoid boundary points
            knots = filtered_wavelengths[knot_idxs]
            
            # Find coefficients by fitting using scipy
            spline_representation = splrep(filtered_wavelengths, filtered_spectrum, s=0, k=3, t=knots) # Test smoothing factor (s) and knots (t)
            # spline_representation = splrep(wavelengths, spectrum, k=3)

            # Extract the B-spline coefficients (c) from the spline representation
            # print(f"spline_representation: {spline_representation}")
            # print(f"Number of knots: {len(spline_representation[0])}")
            # print(f"Knots given: {spline_representation[0]}")
            # print(f"Number of coefficients: {len(spline_representation[1])}")
            # print(f"coefficients: {spline_representation[1]}")
            # print(f"degree of spline (should be 3): {spline_representation[2]}")

            wavelengths_fine = np.linspace(int(min(filtered_wavelengths)), int(max(filtered_wavelengths)), int(len(filtered_wavelengths)))
            # wavelengths_fine = np.linspace(350, 2500, 2151)

            # Evaluate the spline at the  finer wavelengths
            spectrum_fine = splev(wavelengths_fine, spline_representation)
            # print(f"splev: {spectrum_fine}")

            # Compute residuals (differences between original y and spline fit)
            residuals = filtered_spectrum - spectrum_fine

            # Calculate MSE and RMSE
            mse = mean_squared_error(filtered_spectrum, spectrum_fine)
            rmse = np.sqrt(mse)

            # Calculate R-squared
            total_variance = np.sum((filtered_spectrum - np.mean(filtered_spectrum))**2)
            residual_variance = np.sum(residuals**2)
            r_squared = 1 - (residual_variance / total_variance)

            row = [num_knots, mse, rmse, r_squared]
            all_rows.append(row)

            # Print errors and R-squared
            # print(f'residuals: {residuals}')
            # print(f'Mean Squared Error: {mse}')
            # print(f'Root Mean Squared Error: {rmse}')
            # print(f'R-squared: {r_squared}')

            # Plot the original data points and the fitted B-spline curve
            plt.plot(filtered_wavelengths, filtered_spectrum, '-', label='Original Data', color='g')  # Original data points
            plt.plot(wavelengths_fine, spectrum_fine, '--', label='Fitted B-Spline', color='r')  # B-spline curve\
            plt.xlabel('Wavelength')
            plt.ylabel('Spectrum')
            plt.legend()
            plt.savefig(spectra_dir_name + "/knots-" + str(num_knots) + "-vs.png")
            plt.close()

            # ### Plot the difference
            # plt.plot(filtered_wavelengths, filtered_spectrum, '-', label='Original Data', color='g')
            # plt.plot(wavelengths_fine, spectrum_fine - filtered_spectrum, '--', label='Difference', color='r')  # Plot the difference between y2 and y
            # plt.xlabel('Wavelength')
            # plt.ylabel('Spectrum')
            # plt.legend()
            # plt.savefig(dir_name + "/spectra-" + str(i) + "-knots-" + str(num_knots) + "-difference.png")
            # plt.close()
        
        # print(all_rows)
        with open(spectra_dir_name + "/data.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(all_rows)