# PySpark

## 1. Why PySpark?
### Spark Features: 
#### 1.1 In Memory Computation: 
PySpark keeps data in RAM instead of writing intermediate results to disk </br> 

**Traditional Approach:**
```python 
Step 1: Read from disk → Process → Write result to disk
Step 2: Read from disk → Process → Write result to disk
Step 3: Read from disk → Process → Write result to disk
                    ↓
            SLOW (lots of disk I/O)
```

**PySpark (In-Memory) Approach:**
```python 
Step 1: Read from disk → Load into RAM
Step 2: Process in RAM → Keep in RAM
Step 3: Process in RAM → Keep in RAM
Step 4: Process in RAM → Write final result to disk
                    ↓
            FAST (minimal disk I/O)
```
#### 1.2 Lazy Evaluation: 
Spark dosen't execute your code immediately. Instead it builds a plan and only executes when you actually needs the results. 

```python 
df = spark.read.csv('data.csv') # Lazy 
df2 = df.filter(df['age'] > 30 ) # Lazy - not executed yet 
df3 = df2.select('name', 'city') # Lazy - still not executed 
df4 = df3.groupBy('city').count() # Lazy - still waiting............
# At this point, NOTHING has been computed yet!
# spark just has a plan of what to do 

# Now Spark executes everything above 
result = df4.show()
``` 

##### 1.2.1 Why Lazy Evaluation? 
1. **Optimization**: 
Query Planning: spark optimize your entire pipeline before executing 

```python 
df = spark.read.csv("huge_file.csv")
df2 = df.select('name', 'age', 'salary', 'department')
df3 = df2.filter(df2['age'] > 30)
df4 = df3.select('name','department')
result = df4.show() # action 

# Before optimization
# 1. Read all columns from csv
# 2. Select 4 columns 
# 3. Filter rows 
# 4. Select 2 columns 

# After optimization 
# 1. Read only 'name', 'age', 'department' (skip 'salary')
# 2. Filter age>30 while reading 
# 3. return name and department 
```

2. **Avoid Unnecessary Work**: 
```python 
df = spark.read.csv("data.csv")
df2 = df.filter(df['age'] > 30)
df3 = df2.select('name')

# If you never call an action, nothing executes!
# No wasted computation!
```

3. **Efficiency**: 
Combines operations, minimizing data movement 
```python 
# Spark sees the ENTIRE pipeline before executing
df = spark.read.csv("sales.csv")
west_coast = df.filter(df['region'] == 'West')
high_value = west_coast.filter(west_coast['sales'] > 10000)
result = high_value.count()  # Action

# Spark combines both filters into ONE pass:
# Instead of: read → filter region → filter sales
# Optimized: read → filter (region AND sales) in one go
```

#### 1.3 Memory Optimization: 
Process data in stages dosen't load everything at once 

#### 1.4 Fault Tolerance: 
If failure spark knows lineage and can recompute 

## Overview of Spark Infrastructure: 
### Core Components: 
1. Driver (Brain) - The main process that controls the execution 

#### **What it does**:
- Runs your main() program
- Creates SparkContext/SparkSession
- Converts your code into tasks
- Builds the execution plan (DAG - Directed Acyclic Graph)
- Schedules tasks on executors
- Monitors execution
- Collects results 

##### **Contains**:
- SparkContext
- DAG Scheduler
- Task Scheduler
- Block Manager (for driver)

```python 
# This runs on the Driver
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("myapp").getOrCreate()

df = spark.read.csv("data.csv")  # Driver creates execution plan
result = df.filter(df['age'] > 30).count()  # Driver coordinates execution
```

2. Executors (Workers) - Run the actual tasks

#### What they do:
- Execute tasks assigned by the Driver
- Store data for caching/persistence
- Report status back to Driver
- Each executor runs in its own JVM process
#### Contains:
- Task threads (multiple tasks can run in parallel)
- Block Manager (manages cached data)
- Memory for computation and storage

```python 
# Tasks run on Executors
# Example: If you have 3 executors, they split the work
df.filter(...)  # Each executor processes its partition
```

3. Cluster Manager (Resource Allocator) - Allocates resources 
#### What it does:
- Allocates resources (CPU, memory) across applications
- Manages executor lifecycle (start/stop)
- Monitors cluster health
#### Types:
- Standalone - Spark's built-in cluster manager (simple)
- YARN - Hadoop's resource manager (common in Hadoop ecosystems)
- Mesos - General-purpose cluster manager
- Kubernetes - Container orchestration (modern choice)

### Architecture Flow: 
Driver -> Cluster Manager -> Executors -> Task Execution 
```python 
┌─────────────────────────────────────────────────────────────┐
│                         YOUR CODE                           │
│  spark = SparkSession.builder.getOrCreate()                 │
│  df = spark.read.csv("data.csv")                            │
│  result = df.filter(df['age'] > 30).count()                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    DRIVER PROGRAM                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ SparkContext/SparkSession                            │   │
│  │  • Connects to Cluster Manager                       │   │
│  │  • Creates execution plan (DAG)                      │   │
│  │  • Breaks job into stages and tasks                  │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ DAG Scheduler                                        │   │
│  │  • Optimizes execution plan                          │   │
│  │  • Determines stage boundaries                       │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Task Scheduler                                       │   │
│  │  • Assigns tasks to executors                        │   │
│  │  • Manages task retry on failure                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    (Requests Resources)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   CLUSTER MANAGER                           │
│              (YARN / Kubernetes / Standalone)               │
│  • Allocates executors to application                       │
│  • Monitors resource usage                                  │
│  • Manages executor lifecycle                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    (Launches Executors)
                            ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  EXECUTOR 1  │  │  EXECUTOR 2  │  │  EXECUTOR 3  │
│              │  │              │  │              │
│ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │
│ │ Task 1   │ │  │ │ Task 3   │ │  │ │ Task 5   │ │
│ │ Task 2   │ │  │ │ Task 4   │ │  │ │ Task 6   │ │
│ └──────────┘ │  │ └──────────┘ │  │ └──────────┘ │
│              │  │              │  │              │
│ Cache/Memory │  │ Cache/Memory │  │ Cache/Memory │
└──────────────┘  └──────────────┘  └──────────────┘
        ↓                 ↓                 ↓
        └─────────────────┴─────────────────┘
                          ↓
            (Send results back to Driver)
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    DRIVER PROGRAM                           │
│  • Collects results from executors                          │
│  • Aggregates final result                                  │
│  • Returns to your code                                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
                    result = 1500
```

### Step-by-Step Execution Example
Your Code:
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("EmployeeAnalysis") \
    .master("spark://cluster:7077") \
    .getOrCreate()

df = spark.read.csv("employees.csv")
result = df.filter(df['salary'] > 50000).count()
print(result)
```
#### What Happens:

##### Step 1: Driver Initialization
    Driver starts → Creates SparkContext → Connects to Cluster Manager

##### Step 2: Resource Allocation
    Driver: "I need 3 executors with 4GB RAM each"
    Cluster Manager: "Granted! Launching executors on Worker Nodes 1, 2, 3"

##### Step 3: Driver Creates Execution Plan
    Driver analyzes code:
    - Read CSV (transformation - lazy)
    - Filter salary > 50000 (transformation - lazy)
    - count() (action - trigger execution!)

    Driver creates DAG:
    Stage 1: Read CSV + Filter → count per partition
    Stage 2: Aggregate counts from all partitions

##### Step 3: Driver Divides Work into Tasks

    employees.csv has 6 partitions (chunks)

    Driver creates 6 tasks for Stage 1:
    Task 1: Process partition 1 (rows 1-1000)
    Task 2: Process partition 2 (rows 1001-2000)
    Task 3: Process partition 3 (rows 2001-3000)
    Task 4: Process partition 4 (rows 3001-4000)
    Task 5: Process partition 5 (rows 4001-5000)
    Task 6: Process partition 6 (rows 5001-6000)
    Step 5: Task Scheduler Assigns Tasks to Executors

    Executor 1: Gets Task 1, Task 2
    Executor 2: Gets Task 3, Task 4
    Executor 3: Gets Task 5, Task 6
##### Step 6: Executors Execute Tasks

    Executor 1:
    Task 1: Read partition 1 → Filter → Count = 150
    Task 2: Read partition 2 → Filter → Count = 200

    Executor 2:
    Task 3: Read partition 3 → Filter → Count = 180
    Task 4: Read partition 4 → Filter → Count = 170

    Executor 3:
    Task 5: Read partition 5 → Filter → Count = 160
    Task 6: Read partition 6 → Filter → Count = 140

##### Step 7: Executors Send Results to Driver

    Executor 1 → Driver: [150, 200]
    Executor 2 → Driver: [180, 170]
    Executor 3 → Driver: [160, 140]

##### Step 8: Driver Aggregates Results

    Driver: 150 + 200 + 180 + 170 + 160 + 140 = 1000
    Driver returns: result = 1000


##### Communication Flow

    Driver ←──────────────→ Cluster Manager
    ↑                            ↓
    │                     (Launches Executors)
    │                            ↓
    └──────────────→ Executor 1, 2, 3...
        (Heartbeats,         ↓
        Task Results)   (Report status)

#### Key Points:
- Driver and Executors communicate directly (not through Cluster Manager)
- Executors send heartbeats to Driver
- Driver tracks task progress
- If executor dies, Driver reschedules its tasks

#### Fault Tolerance
##### If an Executor fails:
    Executor 2 crashes → Driver detects → Reschedules tasks on Executor 1 or 3

##### How Spark recovers:
- Uses lineage (remembers how data was created)
- Recomputes lost partitions from source
- No data loss!
#### Configuration Example
```python
spark = SparkSession.builder \
    .appName("MyApp") \
    .master("spark://cluster:7077") \  # Cluster Manager address
    .config("spark.executor.instances", "3") \  # 3 executors
    .config("spark.executor.memory", "4g") \    # 4GB per executor
    .config("spark.executor.cores", "2") \      # 2 cores per executor
    .config("spark.driver.memory", "2g") \      # 2GB for driver
    .getOrCreate()
```
##### This creates:
    1 Driver with 2GB RAM
    3 Executors, each with 4GB RAM and 2 CPU cores
    Total cluster capacity: 6 CPU cores, 12GB RAM (for executors)
##### Summary
    YOU WRITE CODE
        ↓
    DRIVER creates execution plan
        ↓
    CLUSTER MANAGER allocates resources
        ↓
    EXECUTORS execute tasks in parallel
        ↓
    DRIVER aggregates results
        ↓
    YOU GET RESULTS

## Spark Connect
With Spark Connect, you only need to install a small, lightweight client library (not the full Spark application), and you can communicate with a remote Spark cluster through APIs.

### What You Need
#### On your machine (client side):
- Just the Spark Connect client library (very small)
- Your programming language (Python, Scala, Java, etc.)
#### Somewhere else (server side):
- A Spark cluster with Spark Connect server running

### Install only the lightweight client
    pip install pyspark-connect

### Connect to remote Spark server
```python 
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .remote("sc://your-spark-server:15002") \
    .getOrCreate()

# Use Spark normally through APIs
df = spark.read.csv("data.csv")
df.show()
```

The client library sends your commands to the remote Spark server, which does all the heavy processing and sends results back to you.

### The Key Difference
**Traditional**: Download 300+ MB of Spark → Run locally

**Spark Connect**: Download ~10 MB client → Connect to remote server

### What This Means Practically
#### Before Spark Connect:
- Your application needed the full Spark software installed (heavy and bulky)
- Your app was tightly connected to the Spark cluster
#### With Spark Connect:
- Your application is lightweight - just needs a small client library
- You send commands over the internet to a Spark server
- The server does all the heavy work and sends back results
- Multiple apps can share the same Spark server
#### Why It's Better
1. **Lighter** - Your application is much smaller
2. **Simpler** - Easier to set up and deploy
3. **Safer** - Updates to Spark won't break your app
4. **Flexible** - Can connect from anywhere (laptops, web apps, notebooks)