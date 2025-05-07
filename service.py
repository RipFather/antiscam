# telegram_service.py
import asyncio
import threading
from concurrent.futures import Future
import time
from getid import TelegramIdFinder, SESSION_NAME, API_ID, API_HASH, errors

_loop: asyncio.AbstractEventLoop = None
_thread: threading.Thread = None
_finder: TelegramIdFinder = None
_initialized = False
_lock = threading.Lock()

def _run_loop(loop: asyncio.AbstractEventLoop):
    global _finder
    asyncio.set_event_loop(loop)
    try:
        _finder = TelegramIdFinder(SESSION_NAME, API_ID, API_HASH)
        loop.run_until_complete(_finder.connect())
        loop.run_forever()
    except errors.SessionPasswordNeededError:
        pass
    except Exception:
        pass
    finally:
        if _finder and _finder.is_ready:
            try:
                loop.run_until_complete(_finder.disconnect())
            except Exception: pass
        if loop.is_running():
            try:
                loop.stop()
            except Exception: pass
        try:
            loop.close()
        except Exception: pass


def initialize_telethon(wait_seconds=7) -> bool:
    global _loop, _thread, _initialized, _finder
    with _lock:
        if _initialized:
            return True

        if _thread is not None and _thread.is_alive():
             pass

        _loop = asyncio.new_event_loop()
        _thread = threading.Thread(target=_run_loop, args=(_loop,), daemon=True)
        _thread.start()

        start_time = time.monotonic()
        while time.monotonic() - start_time < wait_seconds:
            if _finder is not None and _finder.is_ready:
                _initialized = True
                return True
            time.sleep(0.5)

        if _loop and _loop.is_running():
            try:
                _loop.call_soon_threadsafe(_loop.stop)
            except Exception: pass
        _initialized = False
        return False

def shutdown_telethon():
    global _loop, _thread, _initialized, _finder
    with _lock:
        if not _initialized and (_thread is None or not _thread.is_alive()):
            return

        if _loop and _loop.is_running():
            try:
                _loop.call_soon_threadsafe(_loop.stop)
            except Exception: pass

        if _thread:
            try:
                _thread.join(timeout=10)
            except Exception: pass

        _loop = None
        _thread = None
        _finder = None
        _initialized = False


def getids(username: str, timeout: int = 10) -> str:
    global _loop, _finder, _initialized
    if not _initialized or _loop is None or not _loop.is_running() or _finder is None or not _finder.is_ready:
        return None

    coroutine = _finder.get_id_via_bot(username_to_find=username)
    future: Future = asyncio.run_coroutine_threadsafe(coroutine, _loop)

    try:
        result = future.result(timeout=timeout)
        return int(result)
    except (asyncio.TimeoutError, Exception):
        return None