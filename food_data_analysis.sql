-- LOCAL FOOD WASTAGE MANAGEMENT SYSTEM

-- To Create the Database.
DROP DATABASE food_wastage;
CREATE DATABASE food_wastage;

-- Use Database and see all 4 tables.
USE food_wastage;
SHOW TABLES;

-- Check all Data are perfectly Stored or not.
SELECT COUNT(*) AS Total_Providers FROM providers;
SELECT COUNT(*) AS Total_Receivers FROM receivers;
SELECT COUNT(*) AS Total_Food_Listings FROM food_listings;
SELECT COUNT(*) AS Total_Claims FROM claims;

-- See the proper Data Format.
SELECT * FROM providers LIMIT 5;
SELECT * FROM food_listings LIMIT 5;

-- Q1. Identify the top 5 cities with the highest number of food listings.
SELECT 
    Location, 
    COUNT(*) as ListingCount 
FROM food_listings 
GROUP BY Location 
ORDER BY ListingCount DESC 
LIMIT 5;

-- Q2. Find the total volume of food donated by each provider category.
SELECT 
    Provider_Type, 
    SUM(Quantity) as TotalQuantity 
FROM food_listings 
GROUP BY Provider_Type 
ORDER BY TotalQuantity DESC;

-- Q3. What is the success rate of claims (count of each status)?
SELECT 
    Status, 
    COUNT(*) as Total_Claims 
FROM claims 
GROUP BY Status;

-- Q4. Which receiver types claim the most food in terms of total quantity?
SELECT 
    r.Type, 
    SUM(f.Quantity) as Total_Qty 
FROM claims c 
JOIN receivers r ON c.Receiver_ID = r.Receiver_ID 
JOIN food_listings f ON c.Food_ID = f.Food_ID 
GROUP BY r.Type 
ORDER BY Total_Qty DESC;

-- Q5. Find the top 3 highest-contributing providers by their actual names.
SELECT 
    p.Name, 
    SUM(f.Quantity) as Total_Food 
FROM providers p 
JOIN food_listings f ON p.Provider_ID = f.Provider_ID 
GROUP BY p.Name 
ORDER BY Total_Food DESC 
LIMIT 3;

-- Q6. Providers by city: Find the distribution of providers across different cities.
SELECT 
    City, 
    COUNT(*) AS Provider_Count 
FROM providers 
GROUP BY City 
ORDER BY Provider_Count DESC;

-- Q7. Receivers by city: Analyze the presence of receivers in various cities.
SELECT 
    City, 
    COUNT(*) AS Receiver_Count 
FROM receivers 
GROUP BY City 
ORDER BY Receiver_Count DESC;

-- Q8. Most common food type: Identify the most frequently listed food types on the platform.
SELECT 
    Food_Type, 
    COUNT(*) AS Total_Listings 
FROM food_listings 
GROUP BY Food_Type 
ORDER BY Total_Listings DESC;

-- Q9. Average quantity claimed: Calculate the average food quantity successfully claimed per transaction.
SELECT 
    AVG(f.Quantity) AS Avg_Quantity 
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
WHERE c.Status = 'Completed';

-- Q10. Most claimed meal type: Determine which meal type is claimed the most.
SELECT 
    f.Meal_Type, 
    SUM(f.Quantity) AS Claimed_Amount 
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
WHERE c.Status = 'Completed'
GROUP BY f.Meal_Type 
ORDER BY Claimed_Amount DESC;

-- Q11. Most claimed food: Find out which specific food items are claimed the most by volume.
SELECT 
    f.Food_Name, 
    SUM(f.Quantity) AS Total_Claimed 
FROM claims c 
JOIN food_listings f ON c.Food_ID = f.Food_ID 
WHERE c.Status = 'Completed' 
GROUP BY f.Food_Name 
ORDER BY Total_Claimed DESC 
LIMIT 5;

-- Q12. Provider Analysis: Which provider has the highest number of successful (Completed) claims?
SELECT 
    p.Name, 
    COUNT(*) AS Success_Count 
FROM claims c 
JOIN food_listings f ON c.Food_ID = f.Food_ID 
JOIN providers p ON f.Provider_ID = p.Provider_ID 
WHERE c.Status = 'Completed' 
GROUP BY p.Name 
ORDER BY Success_Count DESC 
LIMIT 5;

-- Q13. Total donated quantity by provider: Evaluate the overall efficiency of providers.
SELECT 
    p.Name, 
    SUM(f.Quantity) AS Total_Donated 
FROM providers p 
JOIN food_listings f ON p.Provider_ID = f.Provider_ID 
GROUP BY p.Name 
ORDER BY Total_Donated DESC 
LIMIT 5;

-- Q14. Demand Analysis: Which city has the highest food demand based on the total number of claims made by receivers?
SELECT 
    r.City, 
    COUNT(*) AS Total_Claims 
FROM claims c 
JOIN receivers r ON c.Receiver_ID = r.Receiver_ID 
GROUP BY r.City 
ORDER BY Total_Claims DESC 
LIMIT 5;

-- Q15. Food Waste: Which meal type gets wasted the most (i.e., not completed)?
SELECT 
    f.Meal_Type, 
    SUM(f.Quantity) AS Wasted_Amount 
FROM claims c 
JOIN food_listings f ON c.Food_ID = f.Food_ID 
WHERE c.Status != 'Completed' 
GROUP BY f.Meal_Type 
ORDER BY Wasted_Amount DESC;