import pandas as pd

data = {
    'UserID': [12345, 12345, 67890, 12345],
    'Timestamp': ['2024-06-06 12:34:56', '2024-06-06 12:35:10', '2024-06-06 12:36:00', '2024-06-06 12:37:22'],
    'MessageID': [1, 2, 1, 3],
    'Message': ['Привет!', 'Как дела?', 'Добрый день!', 'Все хорошо, спасибо!']
}
df = pd.DataFrame(data)

df.to_csv('petrovich_log.csv', index=False)