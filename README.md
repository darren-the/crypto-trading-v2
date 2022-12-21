# crypto-trading-v2

:warning: Everything here is currently a draft and will likely change over time

### First steps
- [x] Install apache beam and test a basic bounded pipeline
- [ ] Implement a basic streaming pipeline with splittable DoFns
- [ ] Set up environment (Docker, python formatting, CI/CD)
- [ ] Integrate basic pipeline with Dataflow
- [ ] Integrate Dataflow with Google Big Query/Google Cloud Storage
- [ ] Plan next steps

### Development pipeline
![dev-pipeline](https://user-images.githubusercontent.com/62131073/208803067-e54705c0-bcc2-4d34-8cfd-f885aa33c42b.jpg)

### What will be used
- [Docker](https://www.docker.com/) - Development environment
- [Bitfinex API](https://docs.bitfinex.com/docs) - Historical + live price data
- [Apache Beam](https://beam.apache.org/) - Python library for building data processing pipelines
- [Dataflow](https://cloud.google.com/dataflow) - Google's cloud implementation of Apache Beam
- [Google Big Query](https://cloud.google.com/bigquery) - Data warehouse for storing historical data
- [Flask](https://flask.palletsprojects.com/en/2.2.x/)/[Express.js](https://expressjs.com/) - Back-end API
- [React](https://reactjs.org/) - Front-end application
- [Lightweight Charts](https://github.com/tradingview/lightweight-charts) - Free charting library for price visualization