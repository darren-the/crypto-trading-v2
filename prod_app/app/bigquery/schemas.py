from google.cloud import bigquery


schemas = {
    "FetchCandles": [
        bigquery.SchemaField("exchange", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("timeframe", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("timestamp", "NUMERIC", mode="REQUIRED"),
        bigquery.SchemaField("open", "NUMERIC", mode="REQUIRED"),
        bigquery.SchemaField("close", "NUMERIC", mode="REQUIRED"),
        bigquery.SchemaField("high", "NUMERIC", mode="REQUIRED"),
        bigquery.SchemaField("low", "NUMERIC", mode="REQUIRED"),
    ],
    "AggregateCandles": [
        bigquery.SchemaField("exchange", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("timeframe", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("timestamp", "NUMERIC", mode="REQUIRED"),
        bigquery.SchemaField("candle_timestamp", "NUMERIC", mode="REQUIRED"),
        bigquery.SchemaField("open", "NUMERIC", mode="REQUIRED"),
        bigquery.SchemaField("close", "NUMERIC", mode="REQUIRED"),
        bigquery.SchemaField("high", "NUMERIC", mode="REQUIRED"),
        bigquery.SchemaField("low", "NUMERIC", mode="REQUIRED"),
        bigquery.SchemaField("is_complete", "BOOL", mode="REQUIRED"),
    ]
}
