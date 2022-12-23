# crypto-trading-v2

> :warning: Everything here is currently a draft and will likely change over time

## Getting started
- This project uses [Python 3.7.9](https://www.python.org/downloads/release/python-379/). Other versions _may_ work, but to be safe install this version if you don't have it already.
- For python dependency management, we use __poetry__. Follow the instructions in the [documentation](https://python-poetry.org/docs/) to install poetry and set up dependencies.

    :poop: Setting this up can become tedious so don't worry if you can't get it to work straight away

- Once you've done the steps above, take a look through the sample code [`/sample/1.basic_pipeline.py`](sample/1.basic_pipeline.py) to get an understanding of a basic version of the pipeline. You should also be able to run it locally.

### Quick checklist
A list of to-dos for getting the project going. This will probably be translated into a proper kanban board in notion at some point.
- [x] Install apache beam and test a basic bounded pipeline
- [ ] Implement a basic streaming pipeline with splittable DoFns
- [ ] Set up environment (Docker, python formatting, CI/CD)
- [ ] Integrate basic pipeline with Dataflow
- [ ] Integrate Dataflow with Google Big Query/Google Cloud Storage
- [ ] Plan next steps

### Development pipeline
(More detail required)
![dev-pipeline](https://user-images.githubusercontent.com/62131073/208803067-e54705c0-bcc2-4d34-8cfd-f885aa33c42b.jpg)

### What will be used (Still figuring out)
- [Poetry](https://python-poetry.org/) - Python dependency management
- [Docker](https://www.docker.com/) - For deploying Docker images to google cloud
- [Bitfinex API](https://docs.bitfinex.com/docs) - Historical + live price data
- [Apache Beam](https://beam.apache.org/) - Python library for building data processing pipelines
- [Dataflow](https://cloud.google.com/dataflow) - Google's cloud implementation of Apache Beam
- [Google Big Query](https://cloud.google.com/bigquery) - Data warehouse for storing historical data
- [Flask](https://flask.palletsprojects.com/en/2.2.x/)/[Express.js](https://expressjs.com/) - Back-end API
- [React](https://reactjs.org/) - Front-end application
- [Lightweight Charts](https://github.com/tradingview/lightweight-charts) - Free charting library for price visualization