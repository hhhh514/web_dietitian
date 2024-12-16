import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.metrics.pairwise import cosine_similarity
import pymysql
connection = pymysql.connect(
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
# 菜品特徵
def binary_string_to_numeric(binary_string):
    return [int(bit) for bit in binary_string]

# 更新菜品特徵
dish_features = {
    0: [20, 10, 50, 350, 7.5, 500, 1.2] + binary_string_to_numeric('00110011'),
    1: [15, 20, 60, 450, 6.0, 400, 1.0] + binary_string_to_numeric('01000100'),
    2: [10, 5, 80, 300, 8.0, 300, 1.5] + binary_string_to_numeric('10000000'),
    3: [25, 15, 40, 400, 7.0, 600, 1.3] + binary_string_to_numeric('00010010'),
    4: [30, 20, 30, 500, 6.5, 700, 1.4] + binary_string_to_numeric('00001000'),
}
user_order_history = {
    0: {"早餐": [1], "午餐": [3], "晚餐": [0]},
    1: {"早餐": [1], "午餐": [3], "晚餐": [0]},
    2: {"早餐": [1], "午餐": [3], "晚餐": [0]},
}

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

# 假設已知餐次的菜品
known_meals = {
    "早餐": [1],
    "午餐": [3],
    "晚餐": [0],
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
def recommend_dishes_for_bmi_and_history(height, weight, age, gender):
    bmi = calculate_bmi(height, weight)
    day_recommendations = {}

    for meal_type in ["早餐", "午餐", "晚餐"]:
        meal_dishes = meal_classification[meal_type]  # 使用基於相似度分類的菜品

        # 按餐次生成輸入數據
        top_n = min(len(meal_dishes), 5)
        dish_content_data = np.array([dish_features[dish_id] for dish_id in meal_dishes])
        user_feature_data = np.array([[height, weight, bmi, age, gender]] * len(meal_dishes))

        # 預測
        predictions = model.predict([dish_content_data, user_feature_data]).flatten()

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
    height = data.get("height")
    weight = data.get("weight")
    age = data.get("age")
    gender = data.get("gender")

    if not all([height, weight, age, gender]):
        return jsonify({"error": "All inputs (height, weight, age, gender) are required."}), 400

    # 獲取推薦菜單
    recommendations = recommend_dishes_for_bmi_and_history(height, weight, age, gender)

    # 將推薦菜單的id全部加1
    recommendations = {meal: [dish_id + 1 for dish_id in dish_ids] for meal, dish_ids in recommendations.items()}

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

    return jsonify(result)

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        connection = pymysql.connect(
            host='localhost',
            user='salana',
            password='aas659800123',
            database='test',
            charset='utf8mb4'
        )

        # 從 JSON 請求體中獲取用戶名和密碼
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        try:
            with connection.cursor() as cursor:
                sql = '''SELECT password FROM users WHERE username = %s'''
                cursor.execute(sql, (username,))
                result = cursor.fetchone()

                # 檢查帳號密碼是否匹配
                if result and result[0] == password:
                    return jsonify({"message": "登入成功"})
                else:
                    return jsonify({"error": "登入失敗，請檢查帳號或密碼。"}), 401

        except pymysql.MySQLError as e:
            return jsonify({"error": f"資料庫錯誤: {e}"}), 500

        finally:
            connection.close()

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
