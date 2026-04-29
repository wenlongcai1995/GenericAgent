# R52 - scheduler守护进程修复

## 背景
scheduler.py在启动时因`_lock`端口占用崩溃（NameError: name '_lock' is not defined），导致launchd守护进程持续失败。

## 根因（3层）
1. **代码层**：`try: _lock` / `except NameError:` 无法捕获端口占用异常
   - 正常`importlib.reload()` ok，但`importlib.util.module_from_spec`+`exec_module`（agentmain.py --reflect模式）下第一次执行时无`_lock`，`_lock.bind()`直接抛[Errno 48]
2. **launchd层**：KeepAlive=true导致崩溃后立即重启→再崩溃→无退避→日志爆炸
3. **日志层**：`reflect/scheduler.py`第25行引用全局`LOG_DIR`但未定义→日志写入`temp/None/scheduler.log`

## 修复内容
1. **scheduler.py**: `self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)` + wrap bind in try/except OSError → 端口占用时优雅退出
2. **agentmain.py**: `--reflect`模式下预定义LOG_DIR
3. **launchd plist**: 加`ThrottleInterval<integer>30</integer>`防止重启风暴
4. **记忆更新**: L2新增`[LAUNCHD_PERSISTENCE]`章节+L1同步

## 验证结果
- PID 91471存活，端口45762占用✅
- 120s轮询周期正常运行，stderr无新增错误✅
- 重启测试（unload→load）通过✅