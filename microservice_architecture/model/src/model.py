import pika
import json
import time
import numpy as np
from tensorflow.keras.models import load_model

# Загружаем обученную LSTM модель
model = load_model('lstm_model.h5')

def predict(features):
    # Преобразуем вектор признаков в правильный формат для модели LSTM
    features = np.array(features).reshape(1, 1, -1)
    prediction = model.predict(features)
    predicted_class = np.argmax(prediction, axis=1)
    return predicted_class[0]

# Подключение к RabbitMQ
def main():
    while True:
        try:
            # Установим соединение с RabbitMQ
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            channel = connection.channel()

            # Декларируем очереди для получения и отправки сообщений
            channel.queue_declare(queue='features')
            channel.queue_declare(queue='predictions')

            def callback(ch, method, properties, body):
                # Получаем вектор признаков из очереди
                message = json.loads(body)
                features = message['body']
                message_id = message['id']

                # Предсказание с помощью модели LSTM
                predicted_label = predict(features)

                # Подготовим сообщение с предсказанием
                prediction_message = {
                    'id': message_id,
                    'predicted_label': int(predicted_label)
                }

                # Отправляем предсказание в очередь 'predictions'
                channel.basic_publish(exchange='',
                                      routing_key='predictions',
                                      body=json.dumps(prediction_message))
                print('Отправлено предсказание в очередь')

            # Получаем сообщения из очереди 'features'
            channel.basic_consume(queue='features', on_message_callback=callback, auto_ack=True)

            print('Ожидание сообщений. Для выхода нажмите CTRL+C')
            channel.start_consuming()

        except Exception as error:
            print(f'Не удалось подключиться к очереди: {error}')
            time.sleep(5)

if __name__ == '__main__':
    main()
