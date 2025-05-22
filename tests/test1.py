import unittest
from datetime import datetime, timedelta

# Импортируем нужные переменные и функции из модуля clear_dict
from clear_dict import CLIENT_DICT, CALENDAR_DICT, TIMER_DICT, clear_unused_info, clear_all_dict

# Заглушка для имитации реального объекта клиента
class MockClient:
    def __init__(self):
        self.lst_currant_date = ["2025-05-22"]
        self.dct_currant_time = {"10:00": True}
        self.name_service = "Маникюр"
        self.name_master = "Крапивина Юлия"
        self.date_record = "2025-05-22"
        self.time_record = "13:00"

# Основной класс тестов
class TestUserInfoCleanup(unittest.TestCase):

    # Метод, выполняющийся перед каждым тестом
    def setUp(self):
        # Уникальный идентификатор пользователя для тестов
        self.chat_id = 12345

        # Добавляем фиктивного клиента в словарь
        CLIENT_DICT[self.chat_id] = MockClient()

        # Добавляем фиктивный календарь
        CALENDAR_DICT[self.chat_id] = "Test Calendar"

        # Устанавливаем таймер более чем 60 минут назад, чтобы подходил под условие очистки
        TIMER_DICT[self.chat_id] = datetime.now() - timedelta(days=2)

    # Метод, выполняющийся после каждого теста — очищает все словари
    def tearDown(self):
        CLIENT_DICT.clear()
        CALENDAR_DICT.clear()
        TIMER_DICT.clear()

    # Тест на функцию clear_unused_info
    def test_clear_unused_info(self):
        # Вызываем функцию очистки данных клиента (без удаления объекта)
        clear_unused_info(self.chat_id)

        # Получаем объект клиента
        client = CLIENT_DICT.get(self.chat_id)

        # Проверяем, что объект клиента остался
        self.assertIsNotNone(client)

        # Проверяем, что все его атрибуты очищены
        self.assertIsNone(client.lst_currant_date)
        self.assertIsNone(client.dct_currant_time)
        self.assertIsNone(client.name_service)
        self.assertIsNone(client.name_master)
        self.assertIsNone(client.date_record)
        self.assertIsNone(client.time_record)

        # Проверяем, что календарь был удалён
        self.assertNotIn(self.chat_id, CALENDAR_DICT)

    # Тест на полную очистку всех словарей по chat_id
    def test_clear_all_dict(self):
        # Вызываем функцию, удаляющую всю информацию о пользователе
        clear_all_dict(self.chat_id)

        # Проверяем, что ключ chat_id удалён из всех словарей
        self.assertNotIn(self.chat_id, CLIENT_DICT)
        self.assertNotIn(self.chat_id, CALENDAR_DICT)
        self.assertNotIn(self.chat_id, TIMER_DICT)

    # Тест на корректную работу при попытке очистки несуществующего chat_id
    def test_clear_nonexistent_chat_id(self):
        nonexistent_chat_id = 99999  # Специально выбираем ID, которого нет в словарях

        try:
            # Пытаемся очистить данные по несуществующему chat_id
            clear_unused_info(nonexistent_chat_id)
            clear_all_dict(nonexistent_chat_id)

        # Если возникнет исключение — тест провален
        except Exception as e:
            self.fail(f"Функция вызвала исключение при несуществующем chat_id: {e}")

# Запуск тестов при запуске файла напрямую
if __name__ == '__main__':
    unittest.main()
