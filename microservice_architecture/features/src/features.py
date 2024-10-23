import pika
import numpy as np
import json
import time
from datetime import datetime

# Имитация функции получения признаков для LSTM модели
def generate_lstm_features():
    # Генерация случайных данных, имитирующих признаки для LSTM
    # Например, можешь загрузить реальные данные здесь
    num_features = 5  # Количество признаков, соответствующих твоим данным
    timesteps = 10  # Число временных шагов, например, окно в 10 минут
    features = np.random.randn(timesteps, num_features)
    label = np.random.randint(0, 3)  # 0, 1 или 2 для классов состояния
    return features, label

# Создаем бесконечный цикл для отправки сообщений в очередь
while True:
    try:
        # Получаем признаки для LSTM
        features, label = generate_lstm_features()

        # Создаем подключение по адресу rabbitmq:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        # Создадим очередь y_true
        channel.queue_declare(queue='y_true')
        # Создадим очередь features
        channel.queue_declare(queue='features')

        # Создаем идентификатор сообщения
        message_id = datetime.timestamp(datetime.now())

        # Опубликуем сообщение в очередь y_true (метки классов)
        message_y_true = {
            'id': message_id,
            'body': label
        }
        channel.basic_publish(exchange='',
                              routing_key='y_true',
                              body=json.dumps(message_y_true))
        print('Сообщение с правильным ответом отправлено в очередь')

        # Опубликуем сообщение в очередь features (признаки для LSTM)
        message_features = {
            'id': message_id,
            'body': features.tolist()  # Преобразуем данные в формат для передачи
        }
        channel.basic_publish(exchange='',
                              routing_key='features',
                              body=json.dumps(message_features))
        print('Сообщение с вектором признаков отправлено в очередь')

        # Закроем подключение 
        connection.close()

        # Задержка на 10 секунд перед следующим сообщением
        time.sleep(10)
    except Exception as error:
        print('Не удалось подключиться к очереди: {}'.format(error))
        exit(0)
