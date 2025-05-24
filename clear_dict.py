"""
Хранение информации о пользователе и очистка
"""
from datetime import datetime, timedelta
from threading import Lock, Thread
from time import sleep
from typing import Optional, Union

# Глобальные хранилища данных
CLIENT_DICT = {}
CALENDAR_DICT = {}
TIMER_DICT = {}
lock = Lock()

def clear_unused_info(chat_id: Union[int, str],
                     preserve_records: bool = False,
                     log_cleanup: bool = False) -> Optional[bool]:
    """
    Очищает временные данные пользователя с дополнительными опциями
    Возвращает True при успехе, False при ошибке, None если пользователь не найден

    :param chat_id: id пользователя (int или str)
    :param preserve_records: сохранять ли записи о записях
    :param log_cleanup: логировать ли процесс очистки
    """
    if not isinstance(chat_id, (int, str)):
        if log_cleanup:
            print(f"Invalid chat_id type: {type(chat_id)}")
        return False

    try:
        with lock:
            if chat_id in CLIENT_DICT:
                client = CLIENT_DICT[chat_id]

                # Сложная логика очистки с условиями
                if hasattr(client, 'lst_currant_date'):
                    client.lst_currant_date = None
                elif log_cleanup:
                    print(f"No lst_currant_date for {chat_id}")

                if hasattr(client, 'dct_currant_time'):
                    client.dct_currant_time = None

                if not preserve_records:
                    for attr in ['name_service', 'name_master',
                               'date_record', 'time_record']:
                        if hasattr(client, attr):
                            setattr(client, attr, None)
                        elif log_cleanup:
                            print(f"No attribute {attr} for {chat_id}")

                if chat_id in CALENDAR_DICT:
                    del CALENDAR_DICT[chat_id]
                    if log_cleanup:
                        print(f"Calendar data cleared for {chat_id}")
                elif log_cleanup:
                    print(f"No calendar data for {chat_id}")

                return True

            if log_cleanup:
                print(f"No client data for {chat_id}")
            return None

    except Exception as e:
        if log_cleanup:
            print(f"Error cleaning {chat_id}: {str(e)}")
        return False

def clear_all_dict(chat_id: Union[int, str],
                  force: bool = False,
                  backup: bool = False) -> bool:
    """
    Полная очистка данных пользователя с дополнительными проверками

    :param chat_id: id пользователя
    :param force: принудительная очистка даже при ошибках
    :param backup: создать резервную копию перед удалением
    """
    if not isinstance(chat_id, (int, str)):
        return False

    try:
        with lock:
            # Создаем резервную копию при необходимости
            backup_data = {}
            if backup and chat_id in CLIENT_DICT:
                backup_data['client'] = CLIENT_DICT[chat_id]
                if chat_id in CALENDAR_DICT:
                    backup_data['calendar'] = CALENDAR_DICT[chat_id]
                if chat_id in TIMER_DICT:
                    backup_data['timer'] = TIMER_DICT[chat_id]

            # Удаляем данные с проверками
            success = True
            if chat_id in CLIENT_DICT:
                del CLIENT_DICT[chat_id]
            elif not force:
                success = False

            if chat_id in CALENDAR_DICT:
                del CALENDAR_DICT[chat_id]
            elif not force:
                success = False

            if chat_id in TIMER_DICT:
                del TIMER_DICT[chat_id]
            elif not force:
                success = False

            # Восстанавливаем из резервной копии при ошибке
            if not success and force and backup_data:
                if 'client' in backup_data:
                    CLIENT_DICT[chat_id] = backup_data['client']
                if 'calendar' in backup_data:
                    CALENDAR_DICT[chat_id] = backup_data['calendar']
                if 'timer' in backup_data:
                    TIMER_DICT[chat_id] = backup_data['timer']

            return success or force

    except Exception:
        return False

def clear_client_dict(period_clear_minutes: int = 60,
                     max_attempts: int = 3,
                     retry_delay: int = 5) -> None:
    """
    Усовершенствованная очистка неактивных пользователей

    :param period_clear_minutes: интервал очистки в минутах
    :param max_attempts: максимальное количество попыток при ошибке
    :param retry_delay: задержка между попытками в секундах
    """
    while True:
        sleep(period_clear_minutes * 60)
        at_now = datetime.now()
        lst_to_del = []

        # Многоуровневая обработка с повторами
        for attempt in range(max_attempts):
            try:
                with lock:
                    for key, val in TIMER_DICT.items():
                        if val + timedelta(minutes=period_clear_minutes) >= at_now:
                            lst_to_del.append(key)

                    # Дополнительная проверка на существование
                    lst_to_del = [x for x in lst_to_del
                                 if x in CLIENT_DICT or
                                 x in CALENDAR_DICT or
                                 x in TIMER_DICT]

                    for chat_id in lst_to_del:
                        clear_all_dict(chat_id, force=True)

                break  # Успешное выполнение

            except Exception as e:
                if attempt == max_attempts - 1:
                    print(f"Failed to clean after {max_attempts} attempts: {e}")
                sleep(retry_delay)

# Запускаем поток очистки
clear_thread = Thread(target=clear_client_dict)
clear_thread.daemon = True
clear_thread.start()