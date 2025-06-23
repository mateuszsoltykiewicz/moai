# KafkaManager

## Purpose

The KafkaManager provides async Kafka producer/consumer management for the application:

- Manages Kafka producers and consumers
- Supports dynamic topic configuration and schema validation
- Integrates with metrics, logging, and all components

## Features

- Async, thread-safe
- API for producing and consuming messages
- Prometheus metrics integration

## API

- `POST /kafka/produce` – Produce a message to a Kafka topic
- `GET /kafka/consume` – Consume messages from a Kafka topic

## Usage

Instantiate at app startup with config and inject into components as needed.
