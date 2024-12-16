import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# 假設菜品特徵值 (每道菜的營養分佈：蛋白質、脂肪、碳水化合物)
def binary_string_to_numeric(binary_string):
    return [int(bit) for bit in binary_string]

# 菜品特徵數據
dish_features = {
    0: {"name": "Dish 0", "features": [20, 10, 50, 350, 7.5, 500, 1.2] + binary_string_to_numeric('00110011')},  # 早餐
    1: {"name": "Dish 1", "features": [15, 20, 60, 450, 6.0, 400, 1.0] + binary_string_to_numeric('01000100')},  # 午餐
    2: {"name": "Dish 2", "features": [10, 5, 80, 300, 8.0, 300, 1.5] + binary_string_to_numeric('10000000')},   # 晚餐
    3: {"name": "Dish 3", "features": [25, 15, 40, 400, 7.0, 600, 1.3] + binary_string_to_numeric('00010010')},  # 早餐
    4: {"name": "Dish 4", "features": [30, 20, 30, 500, 6.5, 700, 1.4] + binary_string_to_numeric('00001000')},  # 未分類菜品
}

# 已知的點餐歷史數據（假設知道某些菜品的餐次分類）
known_meals = {
    "早餐": [0, 3],
    "午餐": [1],
    "晚餐": [2],
}

# 1. 計算菜品之間的相似度
dish_ids = list(dish_features.keys())
features = [dish_features[dish_id]["features"] for dish_id in dish_ids]

# 計算菜品之間的相似度矩陣
similarity_matrix = cosine_similarity(features)

# 2. 根據已知的餐次分類來推測未分類菜品
def classify_dishes(known_meals, similarity_matrix, dish_features):
    # 將菜品分類為早餐、午餐或晚餐
    meal_classification = {"早餐": [], "午餐": [], "晚餐": []}
    
    # 對每個菜品，根據與已知餐次菜品的相似度，分配餐次
    for dish_id in dish_ids:
        # 排除已經有餐次分類的菜品
        if dish_id in known_meals["早餐"]:
            meal_classification["早餐"].append(dish_id)
            continue
        elif dish_id in known_meals["午餐"]:
            meal_classification["午餐"].append(dish_id)
            continue
        elif dish_id in known_meals["晚餐"]:
            meal_classification["晚餐"].append(dish_id)
            continue
        
        # 計算這道菜與已知餐次的相似度
        similarities_to_breakfast = similarity_matrix[dish_id, known_meals["早餐"]].mean()
        similarities_to_lunch = similarity_matrix[dish_id, known_meals["午餐"]].mean()
        similarities_to_dinner = similarity_matrix[dish_id, known_meals["晚餐"]].mean()
        
        # 根據相似度分配餐次
        max_similarity = max(similarities_to_breakfast, similarities_to_lunch, similarities_to_dinner)
        if max_similarity == similarities_to_breakfast:
            meal_classification["早餐"].append(dish_id)
        elif max_similarity == similarities_to_lunch:
            meal_classification["午餐"].append(dish_id)
        else:
            meal_classification["晚餐"].append(dish_id)
    
    return meal_classification

# 進行菜品分類
meal_classification = classify_dishes(known_meals, similarity_matrix, dish_features)

# 輸出所有菜品的分類結果
for meal_type, dishes in meal_classification.items():
    print(f"{meal_type} 菜品：")
    for dish_id in dishes:
        print(f"  {dish_features[dish_id]['name']} ({dish_id})")
