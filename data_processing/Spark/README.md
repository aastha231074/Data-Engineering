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

#### 1.3 Avoid Unnecessary Work: 
```python 
df = spark.read.csv("data.csv")
df2 = df.filter(df['age'] > 30)
df3 = df2.select('name')

# If you never call an action, nothing executes!
# No wasted computation!
```

#### 1.4 Efficiency: 
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

#### 1.5 Memory Optimization: 
Process data in stages dosen't load everything at once 

#### 1.6 Fault Tolerance: 
If failure spark knows lineage and can recompute 
