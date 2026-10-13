# Mini-Rag-App
a minimal Rag model, for xxxx (still don't know)

## Requirements
- Python 3.14.7 or later
- the rest is in 'requirements.txt' file

### Install Python using Miniconda:
1. Download Minconda from [here](https://www.anaconda.com/docs/getting-started/installation) 
2. Create a new environment using this Command:
```Bash
    # with 'mini-rag' being the environment's name
    conda create -n mini-rag Python=3.14.7 
```
3. Activate said environment using:
```Bash
    conda activate mini-rag
```

## Install the needed Libraries for this project:
```Bash
pip install -r requirements.txt
```

## Setup the Environment variables:
```Bash
cp .env.exmaple .env
```
and then set your environments variables, like 'OPENAI_API_KEY'.