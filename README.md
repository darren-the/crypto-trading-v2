# crypto-trading-v2

> :warning: Everything here is currently a draft and will likely change over time. Particularly, anything marked with a :question: is not set in stone and still needs to be determined.

## Getting started
- This project uses [Python 3.7.9](https://www.python.org/downloads/release/python-379/) (:question:). Other versions _may_ work, but to be safe install this version if you don't have it already.
- For python dependency management, we use __poetry__ (:question:). Follow the instructions in the [documentation](https://python-poetry.org/docs/) to install poetry and set up dependencies.

    :poop: Setting this up can become tedious so don't worry if you can't get it to work straight away

- Take a look through the sample code [`/sample/1.basic_pipeline.py`](sample/1.basic_pipeline.py) to get an understanding of a basic pipeline. If you completed the above steps, then you should also be able to run it locally.

## Discovery checklist
A list of to-dos for the discovery phase. This will probably be translated into a proper kanban board in [Notion](https://www.notion.so/product) at some point.
- [x] Install apache beam and test a basic bounded pipeline
- [ ] Test creating a dataflow template
- [ ] Run dataflow template through the google cloud API (or an alternate method)
- [ ] Integrate dataflow template with a docker image
- [ ] Test writing to Big Query with dataflow
- [ ] Set up CI/CD pipeline - cloud build trigger, github actions, etc.
- [ ] Plan next steps

## CI/CD Pipeline
![cicd-pipeline](https://user-images.githubusercontent.com/62131073/209456282-58095250-762a-4fcf-a463-d2f5f827622f.jpg)

### Useful links to set up the CI/CD pipeline
- https://cloud.google.com/build/docs/automating-builds/create-manage-triggers
- https://cloud.google.com/dataflow/docs/guides/templates/creating-templates
- https://cloud.google.com/dataflow/docs/guides/templates/running-templates
- https://cloud.google.com/architecture/cicd-pipeline-for-data-processing
- https://github.com/features/actions
- https://docs.docker.com/language/python/configure-ci-cd/

## Data pipeline
(More detail required)
![dev-pipeline](https://user-images.githubusercontent.com/62131073/208803067-e54705c0-bcc2-4d34-8cfd-f885aa33c42b.jpg)

### What will be used (:question:)
- [Poetry](https://python-poetry.org/) - Python dependency management
- [Docker](https://www.docker.com/) - For deploying Docker images to google cloud
- [Bitfinex API](https://docs.bitfinex.com/docs) - Historical + live price data
- [Apache Beam](https://beam.apache.org/) - Python library for building data processing pipelines
- [Dataflow](https://cloud.google.com/dataflow) - Google's cloud implementation of Apache Beam
- [Google Big Query](https://cloud.google.com/bigquery) - Data warehouse for storing historical data
- [Flask](https://flask.palletsprojects.com/en/2.2.x/)/[Express.js](https://expressjs.com/) - Back-end API
- [React](https://reactjs.org/) - Front-end application
- [Lightweight Charts](https://github.com/tradingview/lightweight-charts) - Free charting library for price visualization