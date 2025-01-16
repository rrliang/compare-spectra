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
