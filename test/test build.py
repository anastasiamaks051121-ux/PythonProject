#!/usr/bin/env python3
"""
Smoke/регрессия Android-сборки Unity-игры через adb.
Порт runner.mjs на Python (только стандартная библиотека, ставить ничего не нужно).

Запуск:
    python runner.py --suite suite.json
    python runner.py --apk game.apk --suite suite.json --device emulator-5554
"""

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_SUITE = Path(__file__).with_name("suite.json")

# Строки logcat, которые считаем крашем или ошибкой Unity.
# "E/AndroidRuntime" — только ошибки, а не любые строки с тегом AndroidRuntime.
CRASH_PATTERN = re.compile(
    r"FATAL EXCEPTION|E/AndroidRuntime|UnityException|NullReferenceException"
)


# ---------- adb ----------

def adb(device, *args, allow_failure=False, binary=False):
    """Выполнить команду adb. Если указан device, команда идёт на это устройство."""
    cmd = ["adb"]
    if device:
        cmd += ["-s", device]
    cmd += list(args)

    result = subprocess.run(cmd, capture_output=True, text=not binary)

    if result.returncode != 0 and not allow_failure:
        error = result.stderr.decode(errors="replace") if binary else result.stderr
        raise RuntimeError(f"adb {' '.join(args)} failed: {error or result.stdout}")
    return result


def screenshot(device, file_path):
    """Снять скриншот с устройства и сохранить в PNG."""
    result = adb(device, "exec-out", "screencap", "-p", binary=True)
    file_path.write_bytes(result.stdout)


def assert_package_running(device, package):
    """Проверить, что процесс игры жив (не упал)."""
    result = adb(device, "shell", "pidof", package, allow_failure=True)
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(f"Package is not running: {package}")


def launch_and_measure(device, package, activity):
    """
    Запустить игру и вернуть время старта в мс.
    'am start -W' ждёт первый кадр activity и печатает TotalTime.
    Для Unity это примерно момент появления сплэша, а не готовности игры.
    """
    result = adb(device, "shell", "am", "start", "-W", "-n", f"{package}/{activity}")
    match = re.search(r"TotalTime:\s*(\d+)", result.stdout)
    return int(match.group(1)) if match else None


def collect_logcat(device, result_dir):
    """Сохранить logcat в файл и вернуть последние 20 строк с ошибками."""
    result = adb(device, "logcat", "-d", "-v", "time", allow_failure=True)
    text = result.stdout or ""
    (result_dir / "logcat.txt").write_text(text, encoding="utf-8")
    errors = [line for line in text.splitlines() if CRASH_PATTERN.search(line)]
    return errors[-20:]


# ---------- шаги сценария ----------

def safe_name(text):
    return re.sub(r"[^a-zA-Z0-9_-]", "_", text)


def make_slug(index, name):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return f"{index + 1:02d}-{slug}"


def run_step(step, ctx, step_index):
    action = step.get("action")

    if action == "wait":
        time.sleep(step.get("ms", 1000) / 1000)
    elif action == "tap":
        adb(ctx["device"], "shell", "input", "tap", str(step["x"]), str(step["y"]))
    elif action == "keyevent":
        adb(ctx["device"], "shell", "input", "keyevent", str(step["key"]))
    elif action == "assertPackage":
        assert_package_running(ctx["device"], ctx["package"])
    elif action == "screenshot":
        name = safe_name(step.get("name", f"step-{step_index + 1}"))
        screenshot(ctx["device"], ctx["result_dir"] / f"{ctx['test_slug']}-{name}.png")
    else:
        raise RuntimeError(f"Unsupported action: {action}")


# ---------- основной сценарий ----------

def parse_args():
    parser = argparse.ArgumentParser(description="Android regression runner")
    parser.add_argument("--apk", help="путь к APK для установки")
    parser.add_argument("--suite", default=str(DEFAULT_SUITE), help="файл сценариев")
    parser.add_argument("--device", help="serial устройства (adb devices)")
    parser.add_argument("--out", default="results", help="папка для результатов")
    return parser.parse_args()


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def main():
    args = parse_args()

    suite = json.loads(Path(args.suite).read_text(encoding="utf-8"))
    if "packageName" not in suite or not isinstance(suite.get("tests"), list):
        raise RuntimeError("Suite must contain packageName and tests[]")

    package = suite["packageName"]
    activity = suite.get("activity", "com.unity3d.player.UnityPlayerActivity")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    result_dir = Path(args.out) / timestamp
    result_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "packageName": package,
        "device": args.device or "default adb device",
        "startedAt": now_iso(),
        "tests": [],
    }

    # 1. Устройство подключено?
    adb(args.device, "start-server")
    state = adb(args.device, "get-state", allow_failure=True)
    if state.returncode != 0 or "device" not in state.stdout:
        raise RuntimeError("No Android device is connected or authorized.")

    # 2. Установка и очистка данных
    if args.apk:
        adb(args.device, "install", "-r", str(Path(args.apk).resolve()))
    if suite.get("clearDataBeforeRun"):
        adb(args.device, "shell", "pm", "clear", package)

    # 3. Холодный старт: закрыть игру, очистить старый лог, запустить с замером
    adb(args.device, "shell", "am", "force-stop", package, allow_failure=True)
    adb(args.device, "logcat", "-c", allow_failure=True)
    startup_ms = launch_and_measure(args.device, package, activity)
    report["startupMs"] = startup_ms

    startup_ok = True
    max_startup = suite.get("maxStartupMs")
    if max_startup is not None:
        startup_ok = startup_ms is not None and startup_ms <= max_startup
        report["maxStartupMs"] = max_startup
        report["startupStatus"] = "passed" if startup_ok else "failed"

    time.sleep(suite.get("startupTimeoutMs", 30000) / 1000)

    # 4. Сценарии из suite.json
    ctx = {"device": args.device, "package": package, "result_dir": result_dir}
    for index, test in enumerate(suite["tests"]):
        ctx["test_slug"] = make_slug(index, test.get("name", "test"))
        result = {"name": test.get("name", ctx["test_slug"]), "status": "passed", "steps": []}

        for step_index, step in enumerate(test.get("steps", [])):
            step_result = {"action": step.get("action"), "status": "passed"}
            try:
                run_step(step, ctx, step_index)
            except Exception as error:
                step_result["status"] = "failed"
                step_result["error"] = str(error)
                result["status"] = "failed"
            result["steps"].append(step_result)
            if result["status"] == "failed":
                break  # дальше шаги теста не выполняем

        report["tests"].append(result)

    # 5. Logcat и итог
    errors = collect_logcat(args.device, result_dir)
    report["logcatErrors"] = errors
    report["finishedAt"] = now_iso()

    all_passed = all(t["status"] == "passed" for t in report["tests"])
    report["status"] = "passed" if all_passed and startup_ok and not errors else "failed"

    (result_dir / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "status": report["status"],
        "startupMs": startup_ms,
        "resultDir": str(result_dir),
        "tests": len(report["tests"]),
        "logcatErrors": len(errors),
    }, ensure_ascii=False, indent=2))

    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"Regression runner failed: {error}", file=sys.stderr)
        sys.exit(1)