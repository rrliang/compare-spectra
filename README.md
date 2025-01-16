# Accessing EcoSIS API and Interpolating Spectra using Bspline 
Following the [EcoSIS API tutorial](http://cstars.github.io/ecosis/), this project shows how to downloading and testing spectra from the EcoSIS API using Python, using scipy's bspline interpolator.

### Setting up Python
It is recommended to use a virtual environment to install necessary modules (found in the requirements.txt file). Open a terminal, cd to the place you want to save your virtual environment, and run the following commands:
```
python -m venv ./venv
```
Then, cd into venv/Scripts and run the following command
```
./activate
```
Now, you can pip install all modules in the virtual environment by running the following command:
```
pip install -r requirements.txt
```
Make sure that you are either cd into the project folder containing the requirements.txt, or you can change the path in the command to the absolute path pointing to this project's requirements.

After these steps, you should be all set to run the example python file.

### Querying EcoSIS
#### Dataset
If you want to query the database and extract data, you can follow these steps. First, you will need to figure out information about the dataset(s) that you are interested in accessing. You can search the EcoSIS API using the following link:
https://ecosis.org/api/package/search
Adding request parameters after this link can be done to query the database. The following parameters can be used:
- text - name in dataset you are searching for (String)
- filters - An array of filters which can be used when searching (JSON)
    - Theme
    - Organization
    - Latin Genus
    - Latin Species
    - Common Name
    - Location
- start - Pagination start index (int)
- stop - Pagination stop index (int)

Using this url with the parameters added, you can make a GET request to fetch the dataset information. In Python code, this can be done similar to the following:
```
import requests
import urllib.parse
import json

dataset_url = "https://ecosis.org/api/package/search"

# Define query parameters for dataset search (no filters here, just an example search query)
filters = [
    {"Theme":"Dicot"},
    {"Organization":""},
    {"Latin Genus":""},
    {"Latin Species":""},
    {"Common Name":"northern red oak"},
    {"Location":""},
]

query_json = json.dumps(filters)
query_encoded = urllib.parse.quote(query_json)

params = {
    'text': 'grass',  # the keyword you want to search for
    'start': 0,       # Pagination start index
    'stop': 6,        # Pagination stop index (fetch 6 results in this example)
    'filters': query_encoded  # Example filter: Category = Dicot
}

# Make the GET request to fetch the dataset list
response = requests.get(dataset_url, params=params)

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
```

#### Spectra
Using the dataset id found, you can extract the spectral data. Keep in mind that the EcoSIS datasets come with multiple spectral data, and the code from above may result in multiple datasets, so you will need to loop through all the datasets, and then all the spectral data from each dataset if you want to access all data found from the database query.

Continuing the previous code example, this block of code will access the spectrum in all resulting datasets and convert them into a pandas dataframe.

```
for idx, data_id in enumerate(dataset_ids):
    spectral_url = f"https://ecosis.org/api/package/{data_id}/export?metadata=false"
    
    import pandas as pd
    df = pd.read_csv(spectral_url)
    df = df.apply(pd.to_numeric, errors='coerce')
    wavelengths = df.columns.tolist()

    spectra = df.iloc[1:].values.tolist()
```

From here, you can do the analyze the data however you'd like.