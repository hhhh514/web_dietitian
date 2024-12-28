import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.metrics.pairwise import cosine_similarity
import pymysql
import json
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='salana',
        password='aas659800123',
        database='test',
        charset='utf8mb4'
    )
# 載入模型
model = tf.keras.models.load_model("dish_recommendation_model.h5")
# 建立 Flask 應用程式
app = Flask(__name__)

# 啟用 CORS

CORS(app, resources={r"/recommend": {"origins": "http://localhost:5173"}}, supports_credentials=True)
CORS(app, resources={r"/login": {"origins": "http://localhost:5173"}}, supports_credentials=True)
CORS(app, resources={r"/register": {"origins": "http://localhost:5173"}}, supports_credentials=True)
CORS(app, resources={r"/recipe": {"origins": "http://localhost:5173"}}, supports_credentials=True)
# 菜品口味
def to_flavor_list(sweet, spicy, salty, oily, sour, bitter, light, crispy, fragrant, smoked):
    # 定義對應的風味標識符
    flavor_labels = ['sweet', 'spicy', 'salty', 'oily', 'sour', 'bitter', 'light', 'crispy', 'fragrant', 'smoked']
    # 根據風味標識符的順序，只選擇值為1的風味標籤
    flavor_features = [flavor for flavor, value in zip(flavor_labels, [sweet, spicy, salty, oily, sour, bitter, light, crispy, fragrant, smoked]) if value == 1]
    return flavor_features
connection = get_db_connection()
try:
    dish_features = {}
    with connection.cursor() as cursor:
        query = """
          SELECT dish_id, name, ingredients, food_category, recipe, 
                 sweet, spicy, salty, oily, sour, bitter, light, crispy, fragrant, smoked,
                 calories, protein, carbohydrates, sodium,fiber,fat,vitamins_e,vitamins_c, vitamins_b
          FROM dishes
          
        """
        
        cursor.execute(query)
        # 初始化集合與字典
        remaining_data = {}        # 保留非特徵值欄位資料
        new_dish_id = 0  # 設定新的dish_id從0開始
        
        for row in cursor.fetchall():
            # 重新編號dish_id，從0開始
            dish_id = new_dish_id  
            new_dish_id += 1  # 更新dish_id
            
            # 提取特徵值（第5到最後的欄位）
            flavor_features = tuple(row[5:15])  # 提取 sweet 到 smoked 的欄位
            dish_features[dish_id] = list(row[15:])  # 提取 calories 到 vitamins_b 的欄位
            # 計算16進制值
            flavor_list = to_flavor_list(*flavor_features)

            # 提取剩餘資料（非特徵值）並將16進制風味特徵存入
            remaining_data[dish_id] = {
                "name": row[1],
                "ingredients": row[2],
                "food_category": row[3],
                "recipe": row[4],
                "features_hex": flavor_list  # 存儲為包含1的風味標籤
            }
        for dish_id in list(remaining_data.keys())[:20]:
            dish_info = remaining_data[dish_id]
            print(f"Dish ID: {dish_id}, Name: {dish_info['name']}, Flavor List: {dish_info['features_hex']}")
finally:
    # 關閉連線
    connection.close()

# 更新菜品特徵

user_order_history = {
    0: {"早餐": [3043, 3088, 3294, 3307, 3138, 2916, 3520, 2960], "午餐":[1920, 2539, 2255, 2513, 2033, 1949,1664, 1517, 1007, 1875, 980, 1305,1, 9, 212, 188], "晚餐": [480, 295, 655, 239, 913, 179, 468, 61, 63,1315, 1514, 1870, 1679, 1086, 1053, 1694, 1469,2849, 2724, 2437, 2511, 1752, 1975, 2904, 1983]},
    1: {"早餐": [3145, 3024, 3192, 3687, 3266, 3425, 3790, 3323], "午餐": [2824, 2285, 2323, 2135, 2679, 2329,1831, 1065, 1133, 1006, 1135, 1358, 1101,640, 5, 487, 949, 662, 732, 62], "晚餐": [1354, 1005, 1357, 1011, 1617, 1623, 1820,289, 903, 105, 271, 24, 347,1926, 1993, 1995, 2735, 2707, 2103, 2168]},
    2: {"早餐": [3711, 3644, 3664, 3761, 3023, 3681, 3475, 3181], "午餐": [2080, 2692, 2021, 2282, 1964, 2636, 2578, 1972, 2104, 2108,1089, 1071, 977, 980, 1044, 1014, 1080, 1114,519, 892, 874, 467, 634, 698, 186, 124], "晚餐": [2403, 2217, 2061, 2841,995, 1060, 1068, 1010, 1047, 1117,577, 615, 627, 823, 795, 925]},
}
# 假設用戶的基本數據 (身高 cm，體重 kg，年齡，性別)

# 計算 BMI
def calculate_bmi(height, weight):
    height_m = height / 100
    return weight / (height_m ** 2)

# 推薦函數
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

# 讀取 JSON 文件
with open('menus.json', 'r', encoding='utf-8') as file:
    menu_data = json.load(file)

# 將 JSON 數據放入 known_meals
known_meals = {
    "早餐": menu_data["breakfast_menu"]["早餐"],
    "午餐": menu_data["lunch_menu"]["主食"] + menu_data["lunch_menu"]["主餐"] + menu_data["lunch_menu"]["副餐"],
    "晚餐": menu_data["dinner_menu"]["主食"] + menu_data["dinner_menu"]["主餐"] + menu_data["dinner_menu"]["副餐"],
}


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
# 將菜品ID重新映射
meal_classification = classify_dishes_based_on_similarity(similarity_matrix, known_meals)
def recommend_dishes_for_bmi_and_history(height, weight, age, gender, user_flavor_preferences):
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

        # 根據用戶口味偏好調整預測分數
        for i, dish_id in enumerate(meal_dishes):
            flavor_hex = remaining_data[dish_id]["features_hex"]
            flavor_score = sum(user_flavor_preferences.get(flavor, 0) for flavor in flavor_hex)
            predictions[i] += flavor_score

        # 排序並選出推薦
        top_dishes = np.argsort(predictions)[-top_n:][::-1]
        day_recommendations[meal_type] = [meal_dishes[i] for i in top_dishes]

    return day_recommendations
class Dish:
    def __init__(self, dish_id, name):
        self.dish_id = dish_id
        self.name = name
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid input data"}), 400

    height = data.get("height")
    weight = data.get("weight")
    age = data.get("age")
    gender = data.get("gender")
    flavor_preferences = data.get("flavor_preferences")
    print(flavor_preferences)
    user_flavor_preferences = {
        'spicy': 0,
        'sweet': 0,
        'salty': 0,
        'bitter': 0,
        'sour': 0,
        'oily': 0,
        'light': 0,
        'crispy': 0,
        'fragrant': 0,
        'smoked': 0
    }
    if flavor_preferences:
        for flavor in user_flavor_preferences:
            if flavor in flavor_preferences:
                user_flavor_preferences[flavor] += 100
    if not all([height, weight, age, gender]):
        return jsonify({"error": "All inputs (height, weight, age, gender) are required."}), 400

    # 獲取推薦菜單
    print(height, weight, age, gender, user_flavor_preferences)
    recommendations = recommend_dishes_for_bmi_and_history(height, weight, age, gender, user_flavor_preferences)

    # 將推薦菜單的id全部加1
    recommendations = {meal: [dish_id + 1 for dish_id in dish_ids] for meal, dish_ids in recommendations.items()}

    # 連接到資料庫
    connection = get_db_connection()
    try:
        # 查詢資料庫，並將菜品名稱加入結果中
        result = {}
        with connection.cursor() as cursor:
            for meal, dish_ids in recommendations.items():
                dish_names = []
                for dish_id in dish_ids:
                    # 查詢資料庫以獲取對應菜品名稱
                    query = "SELECT name FROM dishes WHERE dish_id = %s"
                    cursor.execute(query, (dish_id,))
                    dish = cursor.fetchone()
                    if dish:
                        dish_names.append(dish[0])
                    else:
                        dish_names.append(f"Dish with ID {dish_id} not found")
                result[meal] = dish_names
    finally:
        connection.close()

    return jsonify(result)

@app.route('/login', methods=['POST'])
def login():
    try:
        # 連接資料庫
        connection = pymysql.connect(
            host='localhost',
            user='salana',
            password='aas659800123',
            database='test',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor  # 使用 DictCursor 返回字典
        )
        
        # 從 JSON 請求體中獲取用戶名和密碼
        data = request.get_json()
        if not data:
            return jsonify({"error": "無效的請求數據，請檢查輸入。"}), 400

        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({"error": "請提供用戶名和密碼。"}), 400

        with connection.cursor() as cursor:
            # 查詢資料庫
            sql = '''SELECT password, user_id FROM users WHERE username = %s'''
            cursor.execute(sql, (username,))
            result = cursor.fetchone()

            # 檢查帳號密碼是否匹配
            if result and result['password'] == password:
                return jsonify({
                    "message": "登入成功",
                    "user_id": result['user_id']
                })
            else:
                return jsonify({"error": "登入失敗，請檢查帳號或密碼。"}), 401
    except pymysql.MySQLError as e:
        return jsonify({"error": "資料庫操作失敗。", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "伺服器錯誤，請稍後再試。", "details": str(e)}), 500
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

    # 如果不是 POST 方法
    return jsonify({"error": "請使用 POST 方法進行登入。"}), 405
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        # 從 JSON 請求體中獲取資料
        data = request.get_json()

        # 取得資料
        account = data.get("account")
        password = data.get("password")
        name = data.get("name")
        gender = data.get("gender")
        height = float(data.get("height"))
        weight = float(data.get("weight"))
        
        # 計算身體質量指數 (BMI)
        body_type = round(weight / ((height / 100) ** 2), 1) 

        # 檢查是否有缺少的欄位
        missing_fields = []
        for field in ["account", "password", "name", "gender", "height", "weight"]:
            if not data.get(field):
                missing_fields.append(field)

        # 如果有缺少欄位，返回錯誤訊息
        if missing_fields:
            return jsonify({
                "state": "failed",
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # 準備要插入的資料
        response = {
            "state": "success",
            "name": name,
            "gender": gender,
            "height": height,
            "weight": weight,
            "body_type": body_type,
            "account": account,
            "password": password
        }

        # 連接資料庫
        connection = pymysql.connect(
            host='localhost',
            user='salana',
            password='aas659800123',
            database='test',
            charset='utf8mb4'
        )

        try:
            with connection.cursor() as cursor:
                # 插入資料的 SQL 語句
                sql = """
                INSERT INTO users (name, gender, height, weight, body_type, username, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                # 執行 SQL 語句並提交
                cursor.execute(sql, (response['name'], response['gender'], response['height'], response['weight'], response['body_type'], response['account'], response['password']))
                connection.commit()

                print("資料插入成功")
                return jsonify({'state': 'success'}), 200

        except Exception as e:
            print(f"資料插入時發生錯誤: {e}")
            return jsonify({"state": "failed", "error": "資料庫錯誤"}), 500
        
        finally:
            connection.close()

    return jsonify({"state": "failed", "error": "請使用 POST 方法進行註冊。"}), 405
@app.route('/recipe', methods=['POST'])
def get_recipe():
    # 從前端接收菜名
    data = request.get_json()
    dish_name = data.get('dish')
    
    if not dish_name:
        return jsonify({"error": "菜名必須提供"}), 400

    # 連接到資料庫
    connection = pymysql.connect(
            host='localhost',
            user='salana',
            password='aas659800123',
            database='test',
            charset='utf8mb4'
        )


    try:
        with connection.cursor() as cursor:
            # 查詢菜品的做法
            sql = "SELECT recipe FROM dishes WHERE name = %s"
            cursor.execute(sql, (dish_name,))
            result = cursor.fetchone()

            if result:
                # 如果找到了對應的菜品做法
                return jsonify({"recipe": result[0]})
            else:
                # 如果沒找到對應的菜品
                return jsonify({"error": "找不到對應的菜品做法"}), 404

    except Exception as e:
        return jsonify({"error": f"發生錯誤: {str(e)}"}), 500

    finally:
        connection.close()

if __name__ == "__main__":
    app.run(debug=True)
