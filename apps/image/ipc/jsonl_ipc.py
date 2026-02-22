
import json
import struct
import sys
import threading
from typing import BinaryIO, Callable, Dict, Any

class JsonlReader:
    """
    Reads JSON lines from a binary stream (e.g. stdin/stdout).
    """
    def __init__(self, stream: BinaryIO, callback: Callable[[Dict[str, Any]], None]):
        self.stream = stream
        self.callback = callback
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            # Thread will likely block on read, so this is just a flag.
            # In a real app we might close the stream to interrupt.
            pass

    def _run(self):
        # Buffered reader
        buffer = b""
        while self.running:
            try:
                line = self.stream.readline()
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line.decode('utf-8'))
                    self.callback(data)
                except json.JSONDecodeError:
                    # Log error but continue
                    pass
            except ValueError:
                break
            except Exception:
                break


class JsonlWriter:
    """
    Writes JSON lines to a binary stream.
    """
    def __init__(self, stream: BinaryIO):
        self.stream = stream
        self.lock = threading.Lock()

    def send(self, data: Dict[str, Any]):
        with self.lock:
            try:
                line = json.dumps(data) + "\n"
                self.stream.write(line.encode('utf-8'))
                self.stream.flush()
            except Exception:
                # Handle broken pipe etc
                pass
