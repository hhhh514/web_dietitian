import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Concatenate, Input
from sklearn.metrics.pairwise import cosine_similarity
import pymysql
import json
#calories,protein,carbohydrates,sodium,fiber,fat,vitamins_e,vitamins_c,vitamins_b
dish_features = {}
# 建立與 MySQL 資料庫的連線
connection = pymysql.connect(
    host='localhost',
    user='salana',
    password='aas659800123',
    database='test',
    charset='utf8mb4'
)

try:
    with connection.cursor() as cursor:
        # 查詢 dishes 資料表
        query = """
        SELECT dish_id, calories, protein, carbohydrates, sodium, fiber, fat, vitamins_e, vitamins_c, vitamins_b
        FROM dishes
        """
        cursor.execute(query)

        # 讀取資料並存入 dish_features
        dish_features = {}
        for row in cursor.fetchall():
            dish_id = row[0]  # id 作為 key
            features = list(row[1:])  # 其他數據作為 value
            dish_features[dish_id-1] = features

finally:
    # 關閉連線
    connection.close()

# 輸出 dish_features 確認結果
print(dish_features)

# 重新計算特徵維度
feature_dim = len(next(iter(dish_features.values())))

user_order_history = {
    0: {"早餐": [3043, 3088, 3294, 3307, 3138, 2916, 3520, 2960], "午餐":[1920, 2539, 2255, 2513, 2033, 1949,1664, 1517, 1007, 1875, 980, 1305,1, 9, 212, 188], "晚餐": [480, 295, 655, 239, 913, 179, 468, 61, 63,1315, 1514, 1870, 1679, 1086, 1053, 1694, 1469,2849, 2724, 2437, 2511, 1752, 1975, 2904, 1983]},
    1: {"早餐": [3145, 3024, 3192, 3687, 3266, 3425, 3790, 3323], "午餐": [2824, 2285, 2323, 2135, 2679, 2329,1831, 1065, 1133, 1006, 1135, 1358, 1101,640, 5, 487, 949, 662, 732, 62], "晚餐": [1354, 1005, 1357, 1011, 1617, 1623, 1820,289, 903, 105, 271, 24, 347,1926, 1993, 1995, 2735, 2707, 2103, 2168]},
    2: {"早餐": [3711, 3644, 3664, 3761, 3023, 3681, 3475, 3181], "午餐": [2080, 2692, 2021, 2282, 1964, 2636, 2578, 1972, 2104, 2108,1089, 1071, 977, 980, 1044, 1014, 1080, 1114,519, 892, 874, 467, 634, 698, 186, 124], "晚餐": [2403, 2217, 2061, 2841,995, 1060, 1068, 1010, 1047, 1117,577, 615, 627, 823, 795, 925]},
}

# 假設用戶的基本數據 (身高 cm，體重 kg，年齡，性別)
user_data = {
    0: {"height": 170, "weight": 50, "age": 22, "gender": 1},
    1: {"height": 170, "weight": 60, "age": 22, "gender": 1},
    2: {"height": 170, "weight": 85, "age": 22, "gender": 1},
}

# 計算 BMI
def calculate_bmi(height, weight):
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    return bmi

# 計算並將 BMI 加到每個用戶的資料中
for user_id, data in user_data.items():
    data["bmi"] = calculate_bmi(data["height"], data["weight"])

# 提取用戶特徵，包括身高、體重、BMI、年齡和性別
user_features = {
    user_id: [
        data["height"],
        data["weight"],
        data["bmi"],
        data["age"],
        data["gender"],
    ]
    for user_id, data in user_data.items()
}

# 計算菜品之間的相似度矩陣
dish_ids = list(dish_features.keys())
features = [dish_features[dish_id] for dish_id in dish_ids]
similarity_matrix = cosine_similarity(features)

# 基於相似度將菜品分類為早餐、午餐、晚餐
def classify_dishes_based_on_similarity(similarity_matrix, known_meals):
    meal_classification = {"早餐": [], "午餐": [], "晚餐": []}
    
    # 根據已知的餐次分類菜品
    for meal_type, known_dishes in known_meals.items():
        for dish_id in known_dishes:
            meal_classification[meal_type].append(dish_id)
    
    # 分類其他未分類的菜品
    for dish_id in dish_ids:
        if dish_id not in sum(known_meals.values(), []):  # 如果菜品尚未分類
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

# 假設已知餐次的菜品
# 讀取 JSON 文件
with open('menus.json', 'r', encoding='utf-8') as file:
    menu_data = json.load(file)

# 將 JSON 數據放入 known_meals
known_meals = {
    "早餐": menu_data["breakfast_menu"]["早餐"],
    "午餐": menu_data["lunch_menu"]["主食"] + menu_data["lunch_menu"]["主餐"] + menu_data["lunch_menu"]["副餐"],
    "晚餐": menu_data["dinner_menu"]["主食"] + menu_data["dinner_menu"]["主餐"] + menu_data["dinner_menu"]["副餐"],
}

meal_classification = classify_dishes_based_on_similarity(similarity_matrix, known_meals)

# 將菜品ID重新映射
dish_id_mapping = {dish_id: i for i, dish_id in enumerate(dish_features.keys())}
mapped_dish_features = {
    dish_id_mapping[dish_id]: features for dish_id, features in dish_features.items()
}
mapped_user_order_history = {
    user_id: {
        meal_type: [dish_id_mapping[dish_id] for dish_id in dishes]
        for meal_type, dishes in meal_history.items()
    }
    for user_id, meal_history in user_order_history.items()
}

# 參數設置
num_dishes = len(mapped_dish_features)
user_feature_dim = len(next(iter(user_features.values())))

# 模型設計
dish_content_input = Input(shape=(feature_dim,), name='dish_content_input')
user_feature_input = Input(shape=(user_feature_dim,), name='user_feature_input')

dish_content_hidden = Dense(9, activation='relu')(dish_content_input)
user_feature_hidden = Dense(9, activation='relu')(user_feature_input)

concat_features = Concatenate()([dish_content_hidden, user_feature_hidden])
hidden = Dense(64, activation='relu')(concat_features)
hidden = Dense(32, activation='relu')(hidden)
output = Dense(1, activation='sigmoid')(hidden)

model = Model(
    inputs=[dish_content_input, user_feature_input], 
    outputs=output
)
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# 創建訓練數據
X_dish_content, X_user_features, y = [], [], []

for user_id, meal_history in mapped_user_order_history.items():
    for meal_type, ordered_dishes in meal_history.items():
        meal_dishes = meal_classification[meal_type]  # 使用基於相似度分類的菜品

        for dish_id in meal_dishes:
            X_dish_content.append(mapped_dish_features[dish_id])
            X_user_features.append(user_features[user_id])
            y.append(1 if dish_id in ordered_dishes else 0)

X_dish_content = np.array(X_dish_content)
X_user_features = np.array(X_user_features)
y = np.array(y)

# 訓練模型
model.fit(
    [X_dish_content, X_user_features], 
    y, 
    batch_size=8, 
    epochs=10, 
    verbose=1
)

# 推薦函數
def recommend_dishes_for_bmi_and_history(height, weight, age, gender):
    bmi = calculate_bmi(height, weight)
    day_recommendations = {}

    for meal_type in ["早餐", "午餐", "晚餐"]:
        meal_dishes = meal_classification[meal_type]  # 使用基於相似度分類的菜品

        # 按餐次生成輸入數據
        top_n = 1 if meal_type == "早餐" else 3
        dish_content_data = np.array([dish_features[dish_id] for dish_id in meal_dishes])
        user_feature_data = np.array([[height, weight, bmi, age, gender]] * len(meal_dishes))

        # 預測
        predictions = model.predict([dish_content_data, user_feature_data]).flatten()

        # 排序並選出推薦
        top_dishes = np.argsort(predictions)[-top_n:][::-1]
        day_recommendations[meal_type] = [meal_dishes[i] for i in top_dishes]

    return day_recommendations

# 測試
height = 170
weight = 65
age = 25
gender = 1
recommendations = recommend_dishes_for_bmi_and_history(height, weight, age, gender)
print("每日餐次推薦菜品：", recommendations)

model.save("dish_recommendation_model.h5")  # 保存訓練好的模型
model.summary()
