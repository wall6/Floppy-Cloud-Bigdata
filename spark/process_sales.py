from pyspark.sql import SparkSession

from pyspark.sql.functions import regexp_replace, col

from pyspark.sql.types import DoubleType

from pyspark.sql.functions import when

from pyspark.sql.functions import round as spark_round

spark = SparkSession.builder \
    .appName("FloppySalesAnalysis") \
    .getOrCreate()

print("Spark started successfully!")

invoices = spark.read.csv(
    "data/Invoice.csv",
    header=True,
    inferSchema=False,
    multiLine=True
)

items = spark.read.csv(
    "data/item.csv",
    header=True,
    inferSchema=False
)

print("Invoices loaded:")
invoices.show(5)

print("Items loaded:")
items.show(5)

invoice_data = invoices.select(
    "Invoice ID",
    "Customer ID",
    "Customer Name",
    "Total",
    "Quantity",
    "Item Total",
    "Item Price",
    "Product ID"
)

print("Rows with Product ID:")
invoice_data.filter(invoice_data["Product ID"].isNotNull()).show(10)

item_data = items.select(
    "Item ID",
    "Item Name",
    "Purchase Rate"
)

print("Selected invoice columns:")
invoice_data.show(5)

print("Selected item columns:")
item_data.show(5)

# --- Data cleaning: remove rows with no Product ID (drafts / incomplete invoices) ---
invoice_data_clean = invoice_data.filter(invoice_data["Product ID"].isNotNull())

print("Row count before cleaning:", invoice_data.count())
print("Row count after cleaning:", invoice_data_clean.count())

print("Cleaned invoice rows (no Product ID rows removed):")
invoice_data_clean.show(5)

# --- Sanity check: confirm every dropped Invoice ID is actually a draft/no-product row ---
print("Distinct Invoice IDs with missing Product ID (should all be drafts/anomalies):")
invoice_data.filter(invoice_data["Product ID"].isNull()) \
    .select("Invoice ID") \
    .distinct() \
    .show(20, truncate=False)

# --- Join: Invoices (cleaned) -> Items on Product ID = Item ID ---
joined = invoice_data_clean.join(
    item_data,
    invoice_data_clean["Product ID"] == item_data["Item ID"],
    "left"
)

print("Joined invoice + item data:")
joined.show(10)

print("Row count after join:", joined.count())

# --- Sanity check: any joined rows where Item ID didn't match (Product ID exists but no matching Item) ---
print("Unmatched rows (Product ID present but no matching Item ID):")
joined.filter(joined["Item ID"].isNull()).show(10)

# --- Clean currency-formatted columns: strip "PKR " prefix and cast to numeric ---

joined_clean = joined \
    .withColumn(
        "Purchase Rate Clean",
        regexp_replace(col("Purchase Rate"), "PKR ", "").cast(DoubleType())
    ) \
    .withColumn(
        "Item Price Clean",
        col("Item Price").cast(DoubleType())
    ) \
    .withColumn(
        "Item Total Clean",
        col("Item Total").cast(DoubleType())
    ) \
    .withColumn(
        "Quantity Clean",
        col("Quantity").cast(DoubleType())
    )

print("Joined data with cleaned numeric columns:")
joined_clean.select(
    "Invoice ID",
    "Product ID",
    "Item Name",
    "Quantity Clean",
    "Item Price Clean",
    "Item Total Clean",
    "Purchase Rate Clean"
).show(10)

# --- Calculate Revenue, Cost, Profit per line ---

sales_analysis = joined_clean \
    .withColumn("Revenue", col("Item Total Clean")) \
    .withColumn("Cost", col("Purchase Rate Clean") * col("Quantity Clean")) \
    .withColumn("Profit", col("Revenue") - col("Cost"))

print("Sales analysis with Revenue, Cost, Profit:")
sales_analysis.select(
    "Invoice ID",
    "Customer Name",
    "Item Name",
    "Quantity Clean",
    "Revenue",
    "Cost",
    "Profit"
).show(10)

# --- Sanity check: any rows where numeric casting failed (null after cast, non-null before) ---
print("Rows where numeric cast may have failed:")
sales_analysis.filter(
    col("Purchase Rate Clean").isNull() | 
    col("Item Price Clean").isNull() | 
    col("Item Total Clean").isNull()
).select("Invoice ID", "Product ID", "Purchase Rate", "Item Price", "Item Total").show(20, truncate=False)

sales_analysis_tagged = sales_analysis.withColumn(
    "Sale Type",
    when(col("Customer Name") == "Store Use", "Internal Use")
    .when(col("Customer Name") == "Staff", "Staff Use")
    .otherwise("External Sale")
)

print("Sales analysis tagged by type:")
sales_analysis_tagged.select(
    "Invoice ID", "Customer Name", "Sale Type", "Item Name", "Revenue", "Cost", "Profit"
).show(15)

# --- Only external sales count toward "true" business profit ---
external_sales_only = sales_analysis_tagged.filter(col("Sale Type") == "External Sale")

print("Row count - all rows:", sales_analysis_tagged.count())
print("Row count - external sales only:", external_sales_only.count())

print("Total Revenue/Cost/Profit (External Sales Only):")
external_sales_only.selectExpr(
    "sum(Revenue) as Total_Revenue",
    "sum(Cost) as Total_Cost",
    "sum(Profit) as Total_Profit"
).show()

print("Total Revenue/Cost/Profit (ALL rows including internal use):")
sales_analysis_tagged.selectExpr(
    "sum(Revenue) as Total_Revenue",
    "sum(Cost) as Total_Cost",
    "sum(Profit) as Total_Profit"
).show()


external_sales_only.selectExpr(
    "sum(Revenue) as Total_Revenue",
    "sum(Cost) as Total_Cost",
    "sum(Profit) as Total_Profit"
).select(
    spark_round("Total_Revenue", 2).alias("Total_Revenue"),
    spark_round("Total_Cost", 2).alias("Total_Cost"),
    spark_round("Total_Profit", 2).alias("Total_Profit")
).show()