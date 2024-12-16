from flask import Flask, request, jsonify
from flask import Flask, render_template, request, redirect, url_for, flash
import secrets
import pymysql
app = Flask(__name__)

app.secret_key = secrets.token_hex(16)
@app.route('/')
def homepage():
    return render_template('login.html')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        connection = pymysql.connect(
            host='localhost',  
            user='salana', 
            password='aas659800123', 
            database='test',  
            charset='utf8mb4'
        )
        username = request.form['username']
        password = request.form['password']

        try:
            with connection.cursor() as cursor:
                sql = '''SELECT password FROM users WHERE username = %s'''
                cursor.execute(sql, (username,))
                result = cursor.fetchone()

                if result and result[0] == password:
                    return redirect(url_for('home'))  
                else:
                    flash("登入失敗，請檢查帳號或密碼。")
                    
        except pymysql.MySQLError as e:
            flash(f"資料庫錯誤: {e}")
            return redirect(url_for('login'))  

        finally:
            connection.close() 
            
    return render_template('login.html')

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
            user='root', 
            password='', 
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
if __name__ == '__main__':
    app.run(debug=True)
