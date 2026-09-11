# Architecture Documentation — Floppy Cloud Big Data

## What this project is about

This project is a cloud data pipeline I built for Floppy PK, which is my family's computer hardware and accessories shop. Basically I took real sales data (invoices and item/inventory info) that we export from Zoho Books, and built a pipeline that stores it on AWS, processes it using Apache Spark, and gives back useful results like which products make the most profit and which customers buy the most from us.

The point of this project is to show that I understand how cloud storage, cloud compute, and big data processing tools work together, using AWS's free tier so it doesn't cost anything.

## How the data flows

```
Floppy CSV files (Invoice.csv, Item.csv)
              |
              v
      S3 bucket - raw data folder
              |
              v
        EC2 (a virtual computer on AWS)
              |
              v
         Docker (keeps the environment consistent)
              |
              v
      Apache Spark (does the actual processing)
   - removes bad/draft invoice rows
   - joins invoices with item info
   - works out Revenue, Cost, and Profit
   - separates real sales from internal/staff use
   - adds up totals by product and by customer
              |
              v
      S3 bucket - processed data folder
      (the final results get saved here)
```

I made sure the raw CSV files never get changed or deleted — Spark only reads them and saves the results somewhere else. That way if something goes wrong I still have the original data.

## The main parts and why I used them

**Amazon S3 (storage)**
This is where I keep the raw data and the final processed output. I picked S3 because it just works — you don't have to plan how much space you'll need, it scales on its own, and files are encrypted automatically without me having to set anything up.

**Amazon EC2 (compute)**
This is basically a small virtual computer that AWS gives me to run my code on. I used a free-tier instance (t2/t3.micro) running Ubuntu. EC2 is an example of what's called IaaS (Infrastructure as a Service) — AWS handles the actual hardware, but I'm the one who has to set up the operating system and install everything myself, which is different from more "hands-off" services where AWS does more of the work for you.

**Docker**
Docker basically lets me package up Python, Java, Spark, and everything else my code needs into one box, so it runs the same way no matter what. This way I don't have to worry about the EC2 machine having the wrong versions of things installed.

**Apache Spark (PySpark)**
This is the tool that actually cleans and processes the data — removing rows that don't have proper info, joining the invoice data with the item data, and calculating profit. I ran Spark in "local mode," which basically means it runs on just one machine instead of a whole cluster of computers. That's because my dataset is pretty small (160 rows), so I don't need a big cluster — but the same code would technically still work if I had a much bigger dataset and switched to a real cluster later.

**IAM (permissions/security)**
Instead of putting my AWS password/keys directly into the code (which is a bad and risky thing to do), I gave the EC2 instance its own "role" that lets it talk to S3 automatically, without me having to store any keys anywhere. This felt like the safer way to do it once I learned about it.

## How I tried to keep things secure

- No AWS keys are stored anywhere in my code or on GitHub — the EC2 instance uses an IAM role instead.
- S3 automatically encrypts everything stored in it (this is on by default, I didn't have to turn it on).
- I set my EC2 security group so only my own IP address can SSH into it, not the whole internet.
- The real customer names and phone numbers/emails in the invoice data were removed/replaced before putting a sample of the data on GitHub, since we're not supposed to upload sensitive info.

## Keeping costs at $0

- I set up a billing alarm that emails me if AWS charges go over $1, just in case.
- I also turned on AWS's free tier usage alerts.
- I only used free-tier stuff — a small EC2 instance and a tiny amount of S3 storage.
- I make sure to stop the EC2 instance whenever I'm done working, so it doesn't keep running (and possibly costing money) in the background.
- I did have to bump my storage from 8GB to 20GB at one point, but that's still within the free tier limit.

## Problems I ran into (and how I fixed them)

This part was honestly the most annoying but also where I learned the most:

- **The instance kept freezing up.** Turns out the free-tier EC2 instance only has about 1GB of RAM, and Spark tried to use more memory than that, with no backup space (swap) to fall back on. I fixed this by adding a swap file and telling Spark to use less memory.
- **Ran out of disk space, more than once.** Every time I rebuilt my Docker image it downloaded a bunch of stuff, and my 8GB storage filled up fast. I cleaned up unused Docker files to fix it short-term, then just increased the storage to 20GB so it wouldn't keep happening.
- **PySpark install kept failing.** I didn't specify a version number at first, so it tried to install the newest version, which didn't have a ready-made install file and tried to build itself from scratch — and that failed. Fixing it was just a matter of picking a specific, older, more stable version instead.
- **My EC2 (in Mumbai) and my S3 bucket (in the US) are in different AWS regions.** This caused Spark to not find my files at first. I had to explicitly tell Spark which region my S3 bucket was in for it to work properly.
- **My swap file disappeared after I stopped and restarted the instance.** I had to add a line to a config file so it would set the swap back up automatically every time.

## Tools and versions I used

| What | Version |
|---|---|
| EC2 | Ubuntu Server 24.04 LTS, t2.micro/t3.micro (free tier) |
| Python | 3.11 |
| Java | OpenJDK 21 |
| PySpark | 3.5.1 |
| pandas | below version 3.0 |
| Docker | 29.8.0 |
| S3 bucket region | US East (N. Virginia) |
| EC2 region | Asia Pacific (Mumbai) |
