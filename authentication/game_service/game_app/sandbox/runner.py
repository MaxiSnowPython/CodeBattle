import json
from pathlib import Path

def main():
    code_file = Path("/sandbox/code.py")
    tests_file = Path("/sandbox/tests.json")

    user_code = code_file.read_text(encoding="utf-8")
    tests = json.loads(tests_file.read_text(encoding="utf-8"))

    results = []

    user_globals = {}

    try:
        # Выполняем код пользователя
        exec(user_code, user_globals)
    except Exception as e:
        print(json.dumps([{"passed": False, "error": str(e)}]))
        return

    # Проверяем каждый тест
    for test in tests:
        test_input = test.get("input", [])
        expected = test.get("expected")
        passed = False
        test_error = None

        try:
            func = user_globals.get("solution")
            if not func:
                test_error = "Функция 'solution' не найдена"
            else:
                result = func(*test_input)
                passed = result == expected
        except Exception as e:
            test_error = str(e)

        results.append({
            "input": test_input,
            "expected": expected,
            "passed": passed,
            "error": test_error,
        })

    print(json.dumps(results))


if __name__ == "__main__":
    main()
