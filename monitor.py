import os
import shutil
import time
from watchdog.observers.polling import PollingObserver  # Gunakan PollingObserver
from watchdog.events import FileSystemEventHandler

# Path ke direktori web Anda
WEB_DIR = "/home/sinida/public_html"  # Ganti dengan path yang benar
# Path ke salinan aman dari file web Anda
BACKUP_DIR = "/home/sinida/backup"   # Ganti dengan path yang benar

class WebMonitor(FileSystemEventHandler):
    def on_modified(self, event):
        # Jika yang dimodifikasi adalah direktori
        if os.path.isdir(event.src_path):
            print(f'Directory modified: {event.src_path}')
            self.backup_modified_files(event.src_path)  # Backup file yang diubah di dalam direktori
        # Jika yang dimodifikasi adalah file
        else:
            print(f'File modified: {event.src_path}')
            self.restore_file(event.src_path)  # Kembalikan file ke keadaan semula

    def on_created(self, event):
        # Jika yang dibuat adalah file
        if os.path.isfile(event.src_path):
            print(f'File created: {event.src_path}')
            # Cek apakah file ini ada di backup
            relative_path = os.path.relpath(event.src_path, WEB_DIR)
            backup_path = os.path.join(BACKUP_DIR, relative_path)
            
            if not os.path.exists(backup_path):
                print(f'File not in backup, deleting: {event.src_path}')
                os.remove(event.src_path)  # Hapus file baru yang tidak ada di backup
            else:
                self.restore_file(event.src_path)  # Pulihkan file dari backup jika ada
        # Jika yang dibuat adalah folder
        elif os.path.isdir(event.src_path):
            print(f'Folder created: {event.src_path} (deleting...)')
            shutil.rmtree(event.src_path)  # Hapus folder baru beserta isinya

    def on_deleted(self, event):
        print(f'File deleted: {event.src_path}')
        # Coba pulihkan file yang dihapus dari backup
        self.restore_file(event.src_path)

    def on_moved(self, event):
        print(f'File moved: from {event.src_path} to {event.dest_path}')

    def restore_file(self, file_path):
        # Cek apakah file yang diubah ada di backup
        relative_path = os.path.relpath(file_path, WEB_DIR)
        backup_path = os.path.join(BACKUP_DIR, relative_path)

        if os.path.exists(backup_path):
            print(f'Restoring file: {file_path} from backup: {backup_path}')
            shutil.copy2(backup_path, file_path)  # Kembalikan file dari backup
        else:
            print(f'No backup found for: {file_path}')

    def backup_modified_files(self, dir_path):
        # Backup semua file yang diubah di dalam direktori
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                self.restore_file(file_path)  # Kembalikan file ke keadaan semula

if __name__ == "__main__":
    print("Skrip monitor.py mulai berjalan...")
    print(f"Monitoring directory: {WEB_DIR}")
    print(f"Backup directory: {BACKUP_DIR}")

    if not os.path.exists(WEB_DIR):
        print(f"Error: Directory {WEB_DIR} tidak ditemukan!")
        exit(1)

    if not os.path.exists(BACKUP_DIR):
        print(f"Error: Directory {BACKUP_DIR} tidak ditemukan!")
        exit(1)

    event_handler = WebMonitor()
    observer = PollingObserver()  # Gunakan PollingObserver
    observer.schedule(event_handler, path=WEB_DIR, recursive=True)
    observer.start()
    print("Observer started. Monitoring changes...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("Observer stopped.")
    observer.join()