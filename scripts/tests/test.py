from datetime import datetime

current_time = datetime.now()
formatted_time = current_time.strftime('%Y-%m-%d_%H:%M:%S')
print(formatted_time)
