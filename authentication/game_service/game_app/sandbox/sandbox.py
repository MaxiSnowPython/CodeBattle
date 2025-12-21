import json
import subprocess
import tempfile
from pathlib import Path

DOCKER_IMAGE = "python_sandbox_image:latest"

def run_in_sandbox(user_code: str, tests: list):
    """
    Запускает код пользователя в Docker sandbox.
    tests: список тестов [{"input": [...], "expected": ...}, ...]
    Возвращает dict с результатами каждого теста
    """
    results = []
    error = None

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Записываем код пользователя
            code_file = tmpdir_path / "code.py"
            code_file.write_text(user_code, encoding="utf-8")

            # Записываем тесты в JSON
            tests_file = tmpdir_path / "tests.json"
            tests_file.write_text(json.dumps(tests), encoding="utf-8")

            # Запускаем Docker
            cmd = [
                "docker", "run", "--rm",
                "-v", f"{tmpdir_path}:/sandbox",
                DOCKER_IMAGE
            ]
            completed = subprocess.run(
                cmd, capture_output=True, text=True, timeout=5
            )

            output = completed.stdout
            docker_error = completed.stderr

            if completed.returncode != 0:
                error = docker_error
            else:
                try:
                    results = json.loads(output)
                except json.JSONDecodeError:
                    error = "Не удалось распарсить вывод Docker"

    except Exception as e:
        error = str(e)

    return {"results": results, "error": error}
