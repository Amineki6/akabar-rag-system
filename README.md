# Akabar RAG System

Welcome to the **Akabar RAG System** repository! This project is a comprehensive Retrieval-Augmented Generation (RAG) platform, designed with a microservices architecture and built to be deployed seamlessly on Kubernetes.

## Architecture Overview

The system is composed of several independent services working together to provide a seamless conversational and data-retrieval experience:

### Core Services
- **Web Frontend (`web/`)**: The main user interface, serving the interactive chat and RAG components.
- **BFF (Backend-For-Frontend) (`bff/`)**: Acts as the API gateway, managing communication between the frontend and the backend agents.
- **Main Agent (`agent/`)**: The core RAG orchestrator responsible for processing queries, interacting with the vector database, and generating augmented responses.
- **Follow-up Agent (`utils-services/follow-up-agent/`)**: A specialized agent that handles context-aware follow-up questions, utilizing LLMs and MongoDB for session and memory management.
- **Weather API (`utils-services/weather-api/`)**: An auxiliary microservice designed to fetch and format real-time weather data when requested by the agents.

### Data & State Management
- **Data Bank (`data_bank/` & `helper_func/`)**: The repository of raw markdown files and location data that seed the RAG system's knowledge base.
- **Redis (`redis-seeder`)**: Used for fast caching, state management, and intermediate message brokering.

### Infrastructure & Observability
- **Docker Compose**: Used for both local development (`docker-compose.yaml`) and lightweight production (`docker-compose.prod.yaml`) environments.
- **Nginx (`nginx/`)**: The main reverse proxy handling routing and SSL termination.
- **Monitoring (`grafana/`, `prometheus.yml`)**: Integrated Prometheus and Grafana for robust observability and metric tracking across all microservices.
- **Kubernetes & Terraform (`k8s/`, `terraform/`, `terraform-k8s/`)**: Infrastructure-as-Code (IaC) and manifest definitions for scaling the platform on a Kubernetes cluster.

---

## Infrastructure & Kubernetes Migration

This repository features two distinct deployment strategies. While the `main` branch is optimized for straightforward Docker Compose deployments, the `feature/kubernetes-migration` branch introduces a robust, highly scalable infrastructure designed for production environments.

### The `feature/kubernetes-migration` Branch

 This branch contains our complete Infrastructure-as-Code (IaC) and container orchestration setup:

- **Terraform Provisioning**: The entire cloud infrastructure and cluster setup can be provisioned automatically using Terraform (located in `terraform/` and `terraform-k8s/`), ensuring reproducible, version-controlled environments.
- **Kubernetes (K8s) Scalability**: All services have been translated into Kubernetes manifests (`k8s/`). By leveraging K8s, the Akabar system achieves high availability, dynamic auto-scaling under load, and fault-tolerant container orchestration.
- **Secure Secrets Management**: To maintain strict security in production, this branch integrates Kubernetes `SealedSecrets` to safely encrypt and manage sensitive variables (like database credentials and API keys) directly within the cluster.
