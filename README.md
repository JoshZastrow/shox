# Data Processing Script

This project covers a portion of the ETL pipeline for transferring web scraped data into an online database used for an image search engine.

## What Does It Do?
This script reads in a CSV file located in your working directory (file name is specified in the command line as the input argument). It will add a timestamp, then it will assign a tag (label) to each row based on the available tags in `data/meta/tags.csv` and the words in the 'Product Name' column of the CSV. It will also assign an MVP tag based on the tags it assigned via a dictionary lookup.

## Installation

To run the processing script, make sure you have python installed on your computer. This comes with a popular package installer, pip. In the following steps, we're going to clone this repository, create a virtual environment to hold the necessary packages, install them and run the processing script on a demo csv file.

1. Clone this repository to a directory onto your computer
2. Open the terminal, navigate to the directory 

  `$ cd ~/documents/<your-directory-path>`
  
3. Optional Steps: create a virtual environment (see below)

4. Install the required packages: 

  `$ pip install -r requirements.txt'
  
5. run script from terminal: 

  `$ python tag_labels.py DEMO_ZALORA_DRESS.csv`

This will output the processed data to `data/processed/DEMO_ZAORA_DRESS.csv`. You can replace the file name with any other csv file, just make sure the file is located in your current working directory.

## Create a Virtual Environment
Make sure you are still in your project folder in the terminal window. Otherwise, `$ cd ..` to your folder
1. install virtualenv `$ pip install virtualenv`
2. create virtual environment folder `$ virtualenv VENV` <-- creates a folder to hold all the virtual environment packages
3. activate the virtual environemnt `$ source VENV/bin/activate` for macOS, `$VENV\\Scripts\\activate` for windowOS

