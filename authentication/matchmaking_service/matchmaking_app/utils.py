# utils.py
import sys
from io import StringIO
import threading

class TimeoutException(Exception):
    pass

def execute_python_code(code, timeout=5):
    """
    Безопасно выполняет Python код и возвращает результат
    (работает в Django без signal)
    """
    result = {'success': False, 'output': '', 'error': ''}

    def runner():
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        safe_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'sum': sum,
                'max': max,
                'min': min,
                'abs': abs,
                'round': round,
            }
        }

        try:
            exec(code, safe_globals, {})
            result['success'] = True
            result['output'] = captured_output.getvalue().strip()
        except Exception as e:
            result['error'] = str(e)
        finally:
            sys.stdout = old_stdout

    thread = threading.Thread(target=runner)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        result['success'] = False
        result['error'] = f"Код выполняется слишком долго (более {timeout} секунд)"
        # поток продолжает жить, но мы возвращаем таймаут

    return result

def check_answer(user_output, expected_output):
    """
    Проверяет, совпадает ли вывод пользователя с ожидаемым
    """
    user_clean = str(user_output).strip()
    expected_clean = str(expected_output).strip()
    return user_clean == expected_clean
