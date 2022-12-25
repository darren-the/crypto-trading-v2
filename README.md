# crypto-trading-v2

> :warning: Everything here is currently a draft and will likely change over time. Particularly, anything marked with a :question: is not set in stone and still needs to be determined.

## Contents
- [Getting familiar with the project](#getting-familiar-with-the-project)
- [What will be used](#what-will-be-used-question)
- [Setting up your local environment](#setting-up-your-local-environment)
- [Testing code locally during development](#testing-code-locally-during-development-question)
- [Development pipeline](#development-pipeline)
- [CI/CD pipeline](#cicd-pipeline)
    - [How to run a dataflow pipeline without CI/CD (NOT recommended)](#how-to-run-a-dataflow-pipeline-without-cicd-not-recommended)
    - [How to run a dataflow pipeline with CI/CD](#how-to-run-a-dataflow-pipeline-with-cicd)
    - [What's actually happening behind the scenes](#whats-actually-happening-behind-the-scenes)
---

## Getting familiar with the project
Here are several things you should familiarise yourself with before getting started
- Candlestick charts - what are the components of a 'candlestick'?
- [`Sample code`](examples/1.basic_pipeline.py) for the pipeline. Specifically, get familiar with
    - how to fetch candlestick data from an API,
    - and the basics of [Apache Beam](https://beam.apache.org/)
- Understand the main [development pipeline](#development-pipeline) and get an idea of what 'aggregations' and 'transformations' are
- The [CI/CD pipeline](#cicd-pipeline)
    - [Dataflow](https://cloud.google.com/dataflow)
    - [Docker](https://www.docker.com/)

## What will be used (:question:)
- [Docker](https://www.docker.com/) - For deploying Docker images to google cloud
- [Bitfinex API](https://docs.bitfinex.com/docs) - Historical + live price data
- [Apache Beam](https://beam.apache.org/) - Python library for building data processing pipelines
- [Dataflow](https://cloud.google.com/dataflow) - Google's cloud implementation of Apache Beam
- [Google Big Query](https://cloud.google.com/bigquery) - Data warehouse for storing historical data
- [Flask](https://flask.palletsprojects.com/en/2.2.x/)/[Express.js](https://expressjs.com/) - Back-end API
- [React](https://reactjs.org/) - Front-end application
- [Lightweight Charts](https://github.com/tradingview/lightweight-charts) - Free charting library for price visualization

## Setting up your local environment
- This project uses [Python 3.9.13](https://www.python.org/downloads/release/python-3913/). Other versions _may_ work, but to be safe install this version if you don't have it already.
 
    :exclamation: It is recommended that you add Python to PATH. Make sure you tick the checkbox for this when installing python.
- Follow these steps in the command line (using the CLI in VS Code is preferred)
```
# 1. Clone the repository
git clone https://github.com/darren-the/crypto-trading-v2.git

# 2. Navigate to the cloned repository
cd crypto-trading-v2

# 3. Check that you are using python 3.9.13.
which python

# This should show the path to the python 3.9.13 executable.
# If it doesn't, then you will need to add python to PATH.
# Check the link below on how to do this.

# 4. Set up the virtual environment
python -m venv .venv

# 5. Activate the virtual environment.
# The easiest way to do this is to wait for VS Code's prompt which appears after step 4.
# This will automatically activate it for you each time you open VS Code (you may have to restart first).
# For more info on this check the link below.

# Alternatively, use this command (you will need to use it on each new session)
source .venv/Scripts/activate

# 6. Install all required python packages
pip install .

# 7. You should now be ready to go! Test the sample pipeline code
python examples/1.basic_pipeline.py
```
- More info:
    - [How to add Python to PATH](https://realpython.com/add-python-to-path/#:~:text=In%20the%20section%20entitled%20User,until%20it's%20at%20the%20top.)
    - [Using Python environments in VS Code](https://code.visualstudio.com/docs/python/environments)

## Testing code locally during development (:question:)
Although entire runs of our pipeline will be done on Google Cloud with Dataflow, we often may want to run smaller tests of steps that are in the process of being developed.

As of now, the simplest way to do this is by running the command
```
python main.py
```
which writes the output to a text file called 'local_test_data'. Optionally, you can specify the name of the output file yourself with the `--output` argument. So your command may look like this:
```
python main.py --output YOUR_OUTPUT_FILE_NAME
```

## Development pipeline
Below is an end-to-end display of the overall pipeline during the development phase, starting from the left with how data is acquired and going through all the steps that will take place before trading logic is finally tested and visualised.
![dev-pipeline](https://user-images.githubusercontent.com/62131073/208803067-e54705c0-bcc2-4d34-8cfd-f885aa33c42b.jpg)

More detail will be added as each step is developed.

## CI/CD pipeline
Whenever you want to deploy and test the code that you're developing, it can become quite a cumbersome process as you will need to interact with **Google Cloud Platform**, **Github** and **Docker** as part of our workflow.

This CI/CD pipeline automates all the repetitive interactions you would have to make so that each time you make a change, you can deploy and test code with the click of a button.
![cicd-pipeline](https://user-images.githubusercontent.com/62131073/210504285-6440893f-352c-435a-82ef-34cf5b4875d0.jpg)

### How to run a dataflow pipeline without CI/CD (NOT recommended)
Without the automated process displayed above, we would have to do the following every time we make a change:
- First upload all your files to [Google Cloud Shell](https://cloud.google.com/shell)
- Install/update the python packages required to start the pipeline
- Then to run it you would use a command with a ton of configurations such as this
```
python main.py \
    --region DATAFLOW_REGION \
    --output gs://STORAGE_BUCKET/results/outputs \
    --runner DataflowRunner \
    --project PROJECT_ID \
    --temp_location gs://STORAGE_BUCKET/tmp/ \
    --setup_file ./setup.py
```

### How to run a dataflow pipeline with CI/CD
With the automated CI/CD pipeline in place, here is what the steps would look like for us developers.
- Push your changes to a branch
- Go to the [Cloud Build Triggers](https://console.cloud.google.com/gcr/images/crypto-trading-v2/GLOBAL/dataflow-starter?authuser=1) interface. Click the `RUN` button for the 'dataflow-run-trigger'.
![image](https://user-images.githubusercontent.com/62131073/209736965-e6ecc175-9929-4b33-93be-7effcb95f27c.png)

### What's actually happening behind the scenes
1. **A cloud build trigger will detect a push to a branch and rebuild the Docker image if required.** 

    Firstly, the pipeline is going to be executed (in a later step) on a google cloud VM. This VM does not have python packages installed by default, hence we want to use a Docker image with these packages installed already. 

    So in this step, the Docker image will be built (i.e. install any required python packages) _if there has been a change to the python dependencies_. If there has not been any change, then the VM will just reuse the same Docker image and skip rebuilding it.

    This step is specified in the `cloudbuild_docker.yaml` file which builds the Docker image from the `Dockerfile`. The available triggers on GCP can be viewed [here](https://console.cloud.google.com/cloud-build/triggers?referrer=search&authuser=1&project=crypto-trading-v2). In this case, the 'docker-build-trigger' is used.

2. **The Docker image will now be used to start the pipeline**

    The pipeline can now be ran by a manual trigger run (but this could also be automated if we want). 

    This trigger will run the steps in the `cloudbuild_dataflow.yaml` file. In here, it pulls the Docker image that we built from [here](https://console.cloud.google.com/gcr/images/crypto-trading-v2/GLOBAL/dataflow-starter?authuser=1) and then runs a command such as 
    ```
    python main.py \
        --runner DataflowRunner \
        --project crypto-trading-v2 \
        --job_name dataflow-pipeline \
        --regionus-central1 \
        --temp_location gs://crypto-trading-v2-dataflow/temp \
        --setup_file ./setup.py \
        --output gs://crypto-trading-v2-dataflow/placeholder-pipeline-output
    ```
    which submits a dataflow job. Within this step the arguments passed are mandatory pipeline arguments (with the exception of `--output`), but in the future we will probably want to pass in many of our own parameters (such as start and end points for fetching historical data, as well as timeframes, specifying steps we may want to skip, specifying write locations etc.)

An important note is that cloudbuild triggers automatically clone the branch repository which is why it is able to access all our files so easily.