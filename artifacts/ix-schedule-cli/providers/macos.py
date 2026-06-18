"""macOS provider：通过 launchd plist 注册/注销/查询定时任务。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# launchd 星期映射（1=Mon ... 7=Sun）
WEEKDAY_MAP = {"MON": 1, "TUE": 2, "WED": 3, "THU": 4, "FRI": 5, "SAT": 6, "SUN": 7}

PLATFORM_NAME = "macOS"
LABEL_PREFIX = "com.indexed."
LAUNCH_AGENTS_DIR = Path.home() / "Library" / "LaunchAgents"


def _plist_path(job_id: str) -> Path:
    return LAUNCH_AGENTS_DIR / f"{LABEL_PREFIX}{job_id}.plist"


def _python_path() -> str:
    """获取当前 Python 可执行文件路径（launchd 不继承用户 PATH）。"""
    return sys.executable


def register(job: dict, run_command_args: list[str]) -> str:
    """注册 job 到 macOS launchd。返回 label。

    run_command_args: [python_path, main.py_path, 'run', '--job-id', id]
    job: {id, schedule: {kind, time, weekdays}}
    """
    job_id = job["id"]
    label = f"{LABEL_PREFIX}{job_id}"
    sched = job.get("schedule", {})
    kind = sched.get("kind", "daily")
    time = sched.get("time", "09:00")
    hour, minute = time.split(":", 1)

    # 构建 plist
    cal_calendar = {
        "Hour": int(hour),
        "Minute": int(minute),
    }
    if kind == "weekly":
        weekdays = sched.get("weekdays", ["MON"])
        cal_calendar["Weekday"] = [WEEKDAY_MAP.get(d, 1) for d in weekdays]

    plist = _build_plist(label, run_command_args, [cal_calendar])

    LAUNCH_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    plist_path = _plist_path(job_id)
    plist_path.write_text(plist, encoding="utf-8")

    # 加载
    code = subprocess.run(
        ["launchctl", "load", str(plist_path)],
        capture_output=True,
        text=True,
    )
    if code.returncode != 0:
        raise RuntimeError(f"launchctl load 失败: {code.stderr.strip()}")
    return label


def _build_plist(label: str, program_args: list[str], calendars: list[dict]) -> str:
    """构建 launchd plist XML。"""
    import xml.etree.ElementTree as ET

    plist = ET.Element("plist", {"version": "1.0"})
    dict_elem = ET.SubElement(plist, "dict")

    def _key_value(key: str, value_elem_tag: str, value):
        ET.SubElement(dict_elem, "key").text = key
        elem = ET.SubElement(dict_elem, value_elem_tag)
        if value_elem_tag == "array":
            for item in value:
                ET.SubElement(elem, "string").text = str(item)
        else:
            elem.text = str(value)

    def _key_dict(key: str):
        ET.SubElement(dict_elem, "key").text = key
        return ET.SubElement(dict_elem, "dict")

    _key_value("Label", "string", label)
    # ProgramArguments
    ET.SubElement(dict_elem, "key").text = "ProgramArguments"
    args_array = ET.SubElement(dict_elem, "array")
    for arg in program_args:
        ET.SubElement(args_array, "string").text = arg
    # WorkingDirectory（launchd 默认 cwd=/，必须设为 ix-schedule-cli 目录，否则 import 失败）
    _key_value("WorkingDirectory", "string", str(Path(__file__).resolve().parent.parent))
    # StartCalendarInterval
    ET.SubElement(dict_elem, "key").text = "StartCalendarInterval"
    cal_array = ET.SubElement(dict_elem, "array")
    for cal in calendars:
        cal_dict = ET.SubElement(cal_array, "dict")
        for k, v in cal.items():
            ET.SubElement(cal_dict, "key").text = k
            if isinstance(v, list):
                arr = ET.SubElement(cal_dict, "array")
                for item in v:
                    ET.SubElement(arr, "integer").text = str(item)
            else:
                ET.SubElement(cal_dict, "integer").text = str(v)
    # RunAtLoad（可选，不自动跑）
    # StandardOutPath / StandardErrorPath（用 ~/Library/Logs/ 避免 /Volumes/ 外部卷权限问题）
    log_dir = Path.home() / "Library" / "Logs" / "indexed-schedule"
    _key_value("StandardOutPath", "string", str(log_dir / f"{label}.out.log"))
    _key_value("StandardErrorPath", "string", str(log_dir / f"{label}.err.log"))

    ET.indent(plist, space="\t")
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
    xml_str += ET.tostring(plist, encoding="unicode")
    return xml_str


def unregister(label: str) -> None:
    """从 macOS launchd 移除。"""
    job_id = label.replace(LABEL_PREFIX, "")
    plist_path = _plist_path(job_id)
    if plist_path.is_file():
        subprocess.run(
            ["launchctl", "unload", str(plist_path)],
            capture_output=True,
            text=True,
        )
        plist_path.unlink()


def list_tasks() -> list[dict]:
    """列出已注册的 indexed 任务。"""
    if not LAUNCH_AGENTS_DIR.is_dir():
        return []
    tasks = []
    for plist in LAUNCH_AGENTS_DIR.glob(f"{LABEL_PREFIX}*.plist"):
        job_id = plist.stem.replace(LABEL_PREFIX, "")
        tasks.append({"name": plist.stem, "id": job_id})
    return tasks


def get_run_command_args(python_path: str, main_py_path: str, job_id: str) -> list[str]:
    """macOS launchd 需要 ProgramArguments 数组（不是单字符串）。"""
    return [python_path, str(main_py_path), "run", "--job-id", job_id]
