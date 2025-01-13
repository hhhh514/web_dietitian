import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
# 假設你也保存了訓練時的歷史數據
import pickle

# 載入訓練時的歷史數據
with open('history.pkl', 'rb') as f:
    history = pickle.load(f)  # 載入 history.history 字典
test_loss, test_accuracy = model.evaluate(
    [X_dish_content,X_dish_content], 
    y, 
    verbose=0
)
# 繪製訓練損失與準確率
plt.figure(figsize=(12, 5))

# 訓練與驗證的損失圖
plt.subplot(1, 2, 1)
plt.plot(history['loss'], label='Training Loss')
plt.plot(history['val_loss'], label='Validation Loss')
plt.axhline(test_loss, color='r', linestyle='--', label='Test Loss')
plt.title('Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()

# 訓練與驗證的準確率圖
plt.subplot(1, 2, 2)
plt.plot(history['accuracy'], label='Training Accuracy')
plt.plot(history['val_accuracy'], label='Validation Accuracy')
plt.axhline(test_accuracy, color='r', linestyle='--', label='Test Accuracy')
plt.title('Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

plt.tight_layout()
plt.show()
