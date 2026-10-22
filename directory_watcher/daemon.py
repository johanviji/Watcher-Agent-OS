import os
import sys
import json
import time
import struct
import select
import signal
import shutil
import logging
import fnmatch
import ctypes
import platform

LOG_FILE = os.path.join(os.path.dirname(__file__), "watcher.log")
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Platform check to safely handle Windows vs Linux kernel dependencies
if platform.system() == "Windows":
    libc = None
else:
    libc = ctypes.CDLL("libc.so.6", use_errno=True)

IN_CLOSE_WRITE = 0x00000008
IN_MOVED_TO    = 0x00000080
IN_Q_OVERFLOW  = 0x00004000
IN_NONBLOCK    = 0x00000800

EVENT_STRUCT = struct.Struct("iIII")
EVENT_SIZE = EVENT_STRUCT.size

class InotifyDaemon:
    def __init__(self, rules_file, pid_file):
        self.rules_file = rules_file
        self.pid_file = pid_file
        self.rules = []
        self.watch_descriptors = {}
        self.path_to_wd = {}
        self.fd = -1
        self.running = True

        if platform.system() != "Windows":
            signal.signal(signal.SIGHUP, self.reload_rules_signal)
        signal.signal(signal.SIGTERM, self.stop_daemon)
        signal.signal(signal.SIGINT, self.stop_daemon)

    def daemonize(self):
        if platform.system() == "Windows":
            print("Daemonization skipped on Windows. Running in foreground mode.")
            with open(self.pid_file, "w") as f:
                f.write(str(os.getpid()))
            return

        try:
            if os.fork() > 0: 
                sys.exit(0)
        except OSError: 
            sys.exit(1)

        os.chdir("/")
        os.setsid()
        os.umask(0)

        try:
            if os.fork() > 0: 
                sys.exit(0)
        except OSError: 
            sys.exit(1)

        with open(self.pid_file, "w") as f:
            f.write(str(os.getpid()))

        logging.info("Watcher Daemon started successfully with PID %d", os.getpid())

    def load_rules(self):
        if not os.path.exists(self.rules_file):
            self.rules = []
            return

        try:
            with open(self.rules_file, "r") as f:
                self.rules = [r for r in json.load(f) if r.get("active", True)]
        except Exception as e:
            logging.error(f"Failed to parse rules.json: {e}")
            self.rules = []

        if platform.system() == "Windows":
            self.fd = -1
            return

        if self.fd != -1:
            os.close(self.fd)

        self.fd = libc.inotify_init1(IN_NONBLOCK)
        if self.fd < 0: 
            sys.exit(1)

        self.watch_descriptors.clear()
        self.path_to_wd.clear()

        for rule in self.rules:
            path = os.path.expanduser(rule["path"])
            if not os.path.exists(path): 
                continue
            
            wd = libc.inotify_add_watch(self.fd, path.encode('utf-8'), IN_CLOSE_WRITE | IN_MOVED_TO)
            if wd >= 0:
                self.watch_descriptors[wd] = rule["id"]
                self.path_to_wd[path] = wd

    def reload_rules_signal(self, signum, frame):
        self.load_rules()

    def stop_daemon(self, signum, frame):
        self.running = False
        if os.path.exists(self.pid_file): 
            os.remove(self.pid_file)
        sys.exit(0)

    def resolve_name_collision(self, dest_dir, filename):
        base, ext = os.path.splitext(filename)
        counter, target_path = 1, os.path.join(dest_dir, filename)
        while os.path.exists(target_path):
            target_path = os.path.join(dest_dir, f"{base} ({counter}){ext}")
            counter += 1
        return target_path

    def execute_action(self, rule, filename, src_dir):
        src_path = os.path.join(src_dir, filename)
        action = rule["action"]
        dest_dir = os.path.expanduser(rule.get("destination", src_dir))

        os.makedirs(dest_dir, exist_ok=True)
        final_dest = self.resolve_name_collision(dest_dir, filename)

        try:
            if action in {"move", "rename"}:
                shutil.move(src_path, final_dest)
            elif action == "copy":
                shutil.copy2(src_path, final_dest)
            elif action == "compress":
                import zipfile
                zip_path = final_dest + ".zip"
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    zf.write(src_path, filename)
                os.remove(src_path)
            logging.info(f"Executed '{action}' on {src_path} -> {final_dest}")
        except Exception as e:
            logging.error(f"Action error: {e}")

    def run(self):
        self.daemonize()
        self.load_rules()

        # Windows compatibility loop (polling fallback) if tested outside Linux
        if platform.system() == "Windows":
            print("Windows platform detected: Running compatibility polling loop.")
            while self.running:
                time.sleep(2.0)
                self.load_rules()
                for rule in self.rules:
                    src_dir = os.path.expanduser(rule["path"])
                    if os.path.exists(src_dir):
                        for filename in os.listdir(src_dir):
                            if fnmatch.fnmatch(filename, rule.get("pattern", "*")) and not filename.endswith(('.crdownload', '.part', '.tmp')):
                                self.execute_action(rule, filename, src_dir)
            return

        # Native Linux inotify event loop
        while self.running:
            try:
                r, _, _ = select.select([self.fd], [], [], 1.0)
                if not r: 
                    continue
                
                buffer = os.read(self.fd, 4096)
                offset = 0
                while offset < len(buffer):
                    wd, mask, cookie, length = EVENT_STRUCT.unpack_from(buffer, offset)
                    name = buffer[offset + EVENT_SIZE : offset + EVENT_SIZE + length].rstrip(b'\0').decode('utf-8', errors='ignore')
                    offset += EVENT_SIZE + length

                    if mask & IN_Q_OVERFLOW:
                        self.load_rules()
                        break

                    if name.endswith(('.crdownload', '.part', '.tmp')) or not name:
                        continue

                    rule_id = self.watch_descriptors.get(wd)
                    if rule_id:
                        rule = next((r for r in self.rules if r["id"] == rule_id), None)
                        if rule and fnmatch.fnmatch(name, rule.get("pattern", "*")):
                            src_dir = next((p for p, w in self.path_to_wd.items() if w == wd), "")
                            if src_dir:
                                time.sleep(0.2)
                                self.execute_action(rule, name, src_dir)
            except Exception:
                pass

if __name__ == "__main__":
    base = os.path.dirname(__file__)
    InotifyDaemon(os.path.join(base, "rules.json"), os.path.join(base, "watcher.pid")).run()