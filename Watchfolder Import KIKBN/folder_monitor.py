import os
import time
import json
from datetime import datetime
from plyer import notification

# --- Konfigurasi ---
MONITORED_PATHS = [
    r'S:\USER FILESHARING\DOCUMENT CENTER IMPORT\2025\Import KI',
    r'S:\USER FILESHARING\DOCUMENT CENTER IMPORT\2025\Import KBN'
]

CHECK_INTERVAL_SECONDS = 120

# --- Konfigurasi Notifikasi Desktop ---
APP_NAME = "Invoice Monitor"
NOTIFICATION_ICON = None

# known_items_map will now store a dictionary mapping (size, mtime) to full_path for rename detection
# And also the full_path to (size, mtime) for modification detection
# {
#    'path_to_monitor_A': {
#        'unique_file_id_A': 'path/to/file_A',
#        'path/to/file_A': {'size': 123, 'mtime': 12345},
#        ...
#    },
#    ...
# }
known_items_map = {path: {} for path in MONITORED_PATHS}
known_file_stats = {path: {} for path in MONITORED_PATHS} # path -> {full_path: (size, mtime)}
unique_file_ids = {path: {} for path in MONITORED_PATHS} # path -> {(size, mtime): full_path}

RECORD_FILE_PATH = "monitor_record.json"

def load_record():
    if os.path.exists(RECORD_FILE_PATH):
        try:
            with open(RECORD_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Gagal memuat record dari {RECORD_FILE_PATH}: {e}")
            return []
    else:
        return []

def save_record(record):
    try:
        with open(RECORD_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Gagal menyimpan record ke {RECORD_FILE_PATH}: {e}")

def add_record_entry(record, file_path, description, old_path=None):
    no = len(record) + 1
    file_name = os.path.basename(file_path)
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "no": no,
        "file name": file_name,
        "date": date_str,
        "file path": file_path,
        "keterangan": description
    }
    if old_path:
        entry["old path"] = old_path
    record.append(entry)
    save_record(record)

def send_desktop_notification(title, message):
    try:
        notification.notify(
            title=title,
            message=message,
            app_name=APP_NAME,
            app_icon=NOTIFICATION_ICON,
            timeout=10
        )
        print(f"Notifikasi desktop '{title}' berhasil ditampilkan.")
    except Exception as e:
        print(f"Gagal menampilkan notifikasi desktop: {e}")

def get_file_stats(full_path):
    try:
        stats = os.stat(full_path)
        return (stats.st_size, stats.st_mtime)
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error getting stats for {full_path}: {e}")
        return None

def initialize_known_items_for_path(path):
    """Menginisialisasi status file untuk path tertentu."""
    current_path_stats = {}
    current_unique_ids = {}
    for root, dirs, files in os.walk(path):
        for name in files: # Hanya proses file untuk deteksi modifikasi/rename
            full_path = os.path.join(root, name)
            stats = get_file_stats(full_path)
            if stats:
                size, mtime = stats
                current_path_stats[full_path] = (size, mtime)
                current_unique_ids[(size, mtime)] = full_path # Key adalah (size, mtime)

    known_file_stats[path] = current_path_stats
    unique_file_ids[path] = current_unique_ids
    print(f"Inisialisasi: {len(current_path_stats)} file di {path}.")

def monitor_folders():
    record = load_record()

    for path in MONITORED_PATHS:
        print(f"Memulai pemantauan folder: {path}")
        initialize_known_items_for_path(path)

    while True:
        for path in MONITORED_PATHS:
            current_path_stats = {}
            current_unique_ids = {}
            
            new_items_found = []
            modified_items_found = []
            renamed_items_found = []
            
            # Phase 1: Scan current state and identify new/modified files
            for root, dirs, files in os.walk(path):
                for name in files:
                    full_path = os.path.join(root, name)
                    stats = get_file_stats(full_path)
                    
                    if stats:
                        size, mtime = stats
                        current_path_stats[full_path] = (size, mtime)
                        current_unique_ids[(size, mtime)] = full_path

                        old_stats = known_file_stats[path].get(full_path)

                        if full_path not in known_file_stats[path]:
                            # This is a new file or a renamed file
                            # We'll distinguish renamed later in Phase 2
                            new_items_found.append(full_path)
                        elif old_stats and (size, mtime) != old_stats:
                            # File exists and its stats (size or mtime) have changed
                            modified_items_found.append(full_path)
            
            # Phase 2: Identify deleted and potentially renamed files
            deleted_items = []
            for known_path, known_stat_pair in known_file_stats[path].items():
                if known_path not in current_path_stats:
                    # File that existed previously is no longer there
                    deleted_items.append((known_path, known_stat_pair))

            for deleted_path, deleted_stat_pair in deleted_items:
                # Check if a "deleted" file's unique ID (size, mtime) reappears with a new path
                if deleted_stat_pair in current_unique_ids:
                    new_path_for_renamed = current_unique_ids[deleted_stat_pair]
                    if new_path_for_renamed != deleted_path: # Ensure it's not just a false positive
                        renamed_items_found.append((deleted_path, new_path_for_renamed))
                        # Remove from new_items_found if it was mistakenly added as new
                        if new_path_for_renamed in new_items_found:
                            new_items_found.remove(new_path_for_renamed)
                # else:
                #    # If not renamed, then it's genuinely deleted (can add notification if needed)
                #    print(f"File deleted: {deleted_path}")

            # Update known_file_stats and unique_file_ids for the next loop
            known_file_stats[path] = current_path_stats
            unique_file_ids[path] = current_unique_ids
            
            # --- Trigger Notifications ---
            if new_items_found:
                count_new = len(new_items_found)
                folder_name = os.path.basename(path).upper()
                message = f"{folder_name} - {count_new} invoice baru masuk!"
                print(message)
                send_desktop_notification("Invoice Baru Masuk!", message)
                for new_file in new_items_found:
                    add_record_entry(record, new_file, "invoice masuk")

            if modified_items_found:
                for modified_file in modified_items_found:
                    filename = os.path.basename(modified_file)
                    folder_name = os.path.basename(path)
                    message = f"{filename} telah dimodifikasi di {folder_name}!"
                    print(message)
                    send_desktop_notification("Invoice Dimodifikasi", message)
                    add_record_entry(record, modified_file, "invoice dimodifikasi")

            if renamed_items_found:
                for old_path, new_path in renamed_items_found:
                    old_filename = os.path.basename(old_path)
                    new_filename = os.path.basename(new_path)
                    folder_name = os.path.basename(path)
                    message = f"Nama file diubah dari '{old_filename}' menjadi '{new_filename}' di {folder_name}!"
                    print(message)
                    send_desktop_notification("Nama File Invoice Diubah", message)
                    add_record_entry(record, new_path, "nama invoice diubah", old_path=old_path)

            if not new_items_found and not modified_items_found and not renamed_items_found:
                print(f"Tidak ada perubahan di {path}.")

        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    monitor_folders()