# Floppy Cloud Big Data

## Project Overview

This project is all about building a cloud-based big data pipeline using the Floppy dataset ( Floppy is our family owned business ).

The project covers the complete data workflow, including cloud storage, data processing, transformation, and analysis. It is being developed as part of my Al-Nafi Cloud Computing & Big Data presentation.

The main focus is on understanding how cloud computing and big data technologies can be combined to handle and process datasets easy and efficiently.

## Objectives

* Build a complete cloud-based data pipeline
* Store and manage data using AWS s3 bucket. 
* Process and transform data using Apache Spark
* Perform analysis on the dataset
* Understand how the different components of the pipeline work together
* Document the development and results of the project

## Technologies

* AWS
* Amazon S3
* Apache Spark ( local mode ) / PySpark
* Docker
* Git
* GitHub

## Project Structure

* `spark/` — Spark and PySpark processing code
* `docker/` — Docker configuration and related files
* `config/` — Project configuration files
* `docs/` — Documentation and project diagrams
* `sample_data/` — Sample datasets used during development

## Setup Steps

I'll explain this in the order I actually did it, since that's easier to follow than jumping around.

### 1. Running Spark locally (before AWS)

Before touching AWS at all, I first got the Spark script working on my own laptop, just to make sure the logic (cleaning, joining, calculating profit) actually worked before adding cloud stuff on top.

1. Install Python and PySpark (`pip install pyspark==3.5.1 "pandas<3.0"`) — I had to pin the version because the newest PySpark release didn't have a ready-made install and failed to build.
2. Put `Invoice.csv` and `Item.csv` inside a `data/` folder.
3. Run `python spark/process_sales.py`.

### 2. Setting up AWS

1. Made an AWS account and turned on billing alerts so I don't get surprised by charges.
2. Set up a CloudWatch billing alarm that emails me if charges go above $1.
3. Made an IAM user for doing stuff manually in the console, and a separate IAM role (`floppy-ec2-s3-role`) that gets attached to the EC2 instance so it can talk to S3 without me having to put any AWS keys anywhere in the code.
4. Made an S3 bucket with a `raw data` folder and a `processed data` folder, and uploaded the two CSVs into `raw data`.
5. Launched a free-tier EC2 instance (Ubuntu 24.04, t2/t3.micro), attached the IAM role to it, and only allowed SSH access from my own IP, not the whole internet.

### 3. Running everything on EC2 through Docker

1. SSH into the EC2 instance (I used MobaXterm for this).
2. Installed Docker.
3. Put the `Dockerfile` and `process_sales.py` onto the instance.
4. Built the image: `docker build -t floppy-spark-app .`
5. Ran it: `docker run --rm --network host floppy-spark-app`
6. At this point the script reads the raw CSVs straight from S3 and writes the final processed results back into S3, so nothing local is actually needed anymore once it's running on EC2.

## Tools & Libraries

| Tool | Version |
|---|---|
| Python | 3.11 |
| PySpark | 3.5.1 |
| pandas | below 3.0 |
| Java | OpenJDK 21 |
| Docker | 29.8.0 |
| hadoop-aws | 3.3.4 |
| aws-java-sdk-bundle | 1.12.262 |
| EC2 instance | Ubuntu 24.04 LTS, t2/t3.micro (free  tier) |
| S3 bucket region | US East (N. Virginia) |
| EC2 region | Asia Pacific (Mumbai) |

## Cost & Free-Tier Notes

* I only used free-tier stuff the whole time — a small EC2 instance and barely any S3 storage.
* Set up a billing alarm at $1 and turned on free-tier usage alerts as backup, just so I'd know if anything started costing money.
* I always stop the EC2 instance when I'm not actively using it, so it's not sitting there running (and possibly costing money) in the background.
* Had to bump my EC2 storage from 8GB to 20GB at one point because I kept running out of space, but that's still well inside the free tier's 30GB/month limit.
* So far this whole project has cost exactly $0.

## Project Progress

* [x] Git and GitHub setup
* [x] GitHub repository created
* [x] Initial project structure
* [x] Spark data processing
* [x] Data transformation and analysis
* [x] AWS S3 / Data Lake setup
* [x] Docker + EC2 deployment
* [x] Full cloud pipeline (S3 → EC2 → Docker → Spark → S3)
* [ ] Final documentation
* [ ] Project presentation

## Status

**In Development**