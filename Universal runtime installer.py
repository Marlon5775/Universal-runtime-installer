import os
import sys
import ctypes
import locale
import subprocess
import threading
import queue
import traceback
import tempfile
import time
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

def resource_path(relative_path):
    """
    Get absolute path to resource, works for development and for PyInstaller packaging.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class InstallerGUI:
    def __init__(self, root):
        self.root = root
        self.queue = queue.Queue()
        self.cancelled = False

        lang_code = locale.getdefaultlocale()[0]
        if lang_code and lang_code.startswith("de"):
            self.lang = {
                "select_all": "Alle Programme auswählen/abwählen",
                "vc_select_all": "Alle VC Redists auswählen",
                "vc_redist_installs": "VC Redist Installationen",
                "other_installs": "Andere Installationen",
                "ready": "Bereit",
                "install": "Ausgewählte Programme installieren",
                "cancel_install": "Installation abbrechen",
                "close": "Schließen",
                "error": "Fehler",
                "winget_not_installed": "winget ist auf diesem System nicht installiert. Bitte installieren Sie winget und versuchen Sie es erneut.",
                "winget_not_installed_log": "winget ist nicht installiert.",
                "pre_install_cmd_fail": "Pre-Installations-Befehl fehlgeschlagen:\n{errmsg}",
                "pre_install_check_succeeded": "Pre-Installation-Prüfung erfolgreich: {msg}",
                "no_selection": "Keine Auswahl",
                "select_one": "Bitte wählen Sie mindestens ein Programm zur Installation aus.",
                "installation_cancelled": "Installation vom Benutzer abgebrochen.",
                "installation_completed_with_errors": "Installation mit Fehlern abgeschlossen.",
                "installation_completed": "Installation abgeschlossen!",
                "installation_log_end": "Installationsprozess beendet.",
                "winget_version": "winget Version: {version}",
                "checking_winget_updates": "Überprüfe winget Aktualisierungen...",
                "winget_up_to_date": "winget ist aktuell.",
                "winget_update_output": "winget Update Ausgabe: {output}",
                "installing": "Installiere: {prog}",
                "already_installed": "{prog} ist bereits installiert. Überspringe.",
                "error_installing": "Fehler beim Installieren von {prog}: {error}. Versuch, ein Upgrade durchzuführen...",
                "error_upgrading": "Fehler beim Upgrade von {prog}: {error}",
                "upgraded_successfully": "{prog} wurde erfolgreich geupgradet!",
                "output_for": "Ausgabe für {cmd}: {output}",
                "installation_errors": "Installationsfehler",
                "installation_errors_detail": "Die folgenden Programme konnten nicht installiert werden:\n{failed}\n\nBitte prüfen Sie, ob sie bereits installiert sind.",
                "success": "Erfolg",
                "installation_success": "Installation erfolgreich abgeschlossen!"
            }
        else:
            self.lang = {
                "select_all": "Select/Deselect All Programs",
                "vc_select_all": "Select All VC Redists",
                "vc_redist_installs": "VC Redist Installs",
                "other_installs": "Other Installs",
                "ready": "Ready",
                "install": "Install Selected Programs",
                "cancel_install": "Cancel Installation",
                "close": "Close",
                "error": "Error",
                "winget_not_installed": "winget is not installed on this system. Please install winget and try again.",
                "winget_not_installed_log": "winget not installed.",
                "pre_install_cmd_fail": "Pre-installation command failed:\n{errmsg}",
                "pre_install_check_succeeded": "Pre-installation check succeeded: {msg}",
                "no_selection": "No Selection",
                "select_one": "Please select at least one program to install.",
                "installation_cancelled": "Installation cancelled by user.",
                "installation_completed_with_errors": "Installation completed with errors.",
                "installation_completed": "Installation completed!",
                "installation_log_end": "Installation process ended.",
                "winget_version": "winget version: {version}",
                "checking_winget_updates": "Checking for winget updates...",
                "winget_up_to_date": "winget is up to date.",
                "winget_update_output": "winget update output: {output}",
                "installing": "Installing: {prog}",
                "already_installed": "{prog} is already installed. Skipping.",
                "error_installing": "Error installing {prog}: {error}. Trying upgrade...",
                "error_upgrading": "Error upgrading {prog}: {error}",
                "upgraded_successfully": "{prog} upgraded successfully!",
                "output_for": "Output for {cmd}: {output}",
                "installation_errors": "Installation Errors",
                "installation_errors_detail": "The following programs failed to install:\n{failed}\n\nCheck if these are already installed.",
                "success": "Success",
                "installation_success": "Installation has completed successfully!"
            }

        self.programs = [
            {"name": "DirectX", "command": ["winget install Microsoft.DirectX --force"], "group": "other"},
            {"name": "Java Runtime", "command": ["winget install Oracle.JavaRuntimeEnvironment --force"], "group": "other"},
            {"name": "Net Runtime 8", "command": ["winget install Microsoft.DotNet.DesktopRuntime.8 --force"], "group": "other"},
            {"name": "OpenAL", "command": ["winget install OpenAL.OpenAL --force"], "group": "other"},
            {"name": "XNA Redist", "command": ["winget install Microsoft.XNARedist --force"], "group": "other"},
            {"name": "VC - Redist 2010", "command": [
                "winget install Microsoft.VCRedist.2010.x64 --force",
                "winget install Microsoft.VCRedist.2010.x86 --force"
            ], "group": "vc"},
            {"name": "VC - Redist 2012", "command": [
                "winget install Microsoft.VCRedist.2012.x64 --force",
                "winget install Microsoft.VCRedist.2012x86 --force"
            ], "group": "vc"},
            {"name": "VC - Redist 2013", "command": [
                "winget install Microsoft.VCRedist.2013.x64 --force",
                "winget install Microsoft.VCRedist.2013.x86 --force"
            ], "group": "vc"},
            {"name": "VC - Redist 2015-2022", "command": [
                "winget install Microsoft.VCRedist.2015+.x64 --force",
                "winget install Microsoft.VCRedist.2015+.x86 --force"
            ], "group": "vc"}
        ]

        self.vars = [ttk.BooleanVar(value=True) for _ in self.programs]
        self.select_all_var = ttk.BooleanVar(value=True)
        self.vc_select_all_var = ttk.BooleanVar(value=True)
        self.setup_ui()

    def setup_ui(self):
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill='x')
        master_chk = ttk.Checkbutton(
            top_frame,
            text=self.lang["select_all"],
            variable=self.select_all_var,
            command=self.toggle_all
        )
        master_chk.pack(anchor='w')

        group_frame = ttk.Frame(self.root, padding=10)
        group_frame.pack(fill='both', expand=True)

        vc_frame = ttk.Frame(group_frame)
        vc_frame.grid(row=0, column=0, sticky="nw")
        vc_label = ttk.Label(vc_frame, text=self.lang["vc_redist_installs"], font=("Arial", 10, "bold"))
        vc_label.pack(anchor="w")
        vc_master_chk = ttk.Checkbutton(
            vc_frame,
            text=self.lang["vc_select_all"],
            variable=self.vc_select_all_var,
            command=self.toggle_vc_all
        )
        vc_master_chk.pack(anchor="w", padx=(10, 0))
        for i, program in enumerate(self.programs):
            if program.get("group", "other") == "vc":
                chk = ttk.Checkbutton(vc_frame, text=program['name'], variable=self.vars[i])
                chk.pack(anchor="w", padx=(20, 0))

        other_frame = ttk.Frame(group_frame)
        other_frame.grid(row=0, column=1, sticky="ne", padx=(20, 0))
        other_label = ttk.Label(other_frame, text=self.lang["other_installs"], font=("Arial", 10, "bold"))
        other_label.pack(anchor="w")
        for i, program in enumerate(self.programs):
            if program.get("group", "other") != "vc":
                chk = ttk.Checkbutton(other_frame, text=program['name'], variable=self.vars[i])
                chk.pack(anchor="w", padx=(10, 0))

        progress_frame = ttk.Frame(self.root, padding=10)
        progress_frame.pack(fill='both', expand=True)
        self.progress_current = ttk.Progressbar(progress_frame, orient='horizontal', length=300, mode='determinate')
        self.progress_current.pack(pady=5)
        self.progress_total = ttk.Progressbar(progress_frame, orient='horizontal', length=300, mode='determinate')
        self.progress_total.pack(pady=5)
        self.status_label = ttk.Label(progress_frame, text=self.lang["ready"])
        self.status_label.pack(pady=5)

        log_frame = ttk.Frame(self.root, padding=10)
        log_frame.pack(fill='both', expand=True)
        self.logger = ttk.ScrolledText(log_frame, height=10, wrap='word')
        self.logger.pack(fill='both', expand=True)

        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill='both', expand=True)
        self.install_button = ttk.Button(btn_frame, text=self.lang["install"], command=self.start_installation)
        self.install_button.pack(side='left', padx=5)
        self.cancel_button = ttk.Button(btn_frame, text=self.lang["cancel_install"], command=self.cancel_installation, state=ttk.DISABLED)
        self.cancel_button.pack(side='left', padx=5)
        self.close_button = ttk.Button(btn_frame, text=self.lang["close"], command=self.on_close)
        self.close_button.pack(side='right', padx=5)

    def on_close(self):
        """Close the application."""
        self.root.destroy()

    def toggle_all(self):
        state = self.select_all_var.get()
        for var in self.vars:
            var.set(state)
        self.vc_select_all_var.set(state)

    def toggle_vc_all(self):
        state = self.vc_select_all_var.get()
        for i, program in enumerate(self.programs):
            if program.get("group", "other") == "vc":
                self.vars[i].set(state)

    def cancel_installation(self):
        self.cancelled = True
        self.append_log(self.lang["installation_cancelled"])
        self.install_button.config(state=ttk.NORMAL)
        self.cancel_button.config(state=ttk.DISABLED)
        self.close_button.config(state=ttk.NORMAL)

    def append_log(self, message):
        """Append a message to the log widget and log it to a file."""
        log_line = message + "\n"
        self.logger.insert('end', log_line)
        self.logger.see('end')
        try:
            with open("installer_log.txt", "a", encoding="utf-8") as log_file:
                log_file.write(log_line)
        except Exception as e:
            print("Failed to write to log file:", e)

    def process_queue(self):
        """Process queued messages to update the UI."""
        try:
            while True:
                msg = self.queue.get_nowait()
                if msg["type"] == "status":
                    self.status_label.config(text=msg["message"])
                elif msg["type"] == "log":
                    self.append_log(msg["message"])
                elif msg["type"] == "progress_current":
                    self.progress_current['value'] = msg["value"]
                elif msg["type"] == "progress_total":
                    self.progress_total['value'] = msg["value"]
        except queue.Empty:
            pass
        self.root.after(100, self.process_queue)

    def run_command(self, command):
        """Execute a shell command and return its output, error, and exit code."""
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        return output, error, process.returncode

    def check_and_update_winget(self):
        """Check if winget is installed and update it if necessary."""
        self.append_log(self.lang["checking_winget_updates"])
        output, error, code = self.run_command("winget --version")
        if code != 0:
            messagebox.showerror(self.lang["error"], self.lang["winget_not_installed"])
            self.append_log(self.lang["winget_not_installed_log"])
            return False
        winget_version = output.decode('utf-8', errors='replace').strip()
        self.append_log(self.lang["winget_version"].format(version=winget_version))
        self.append_log(self.lang["checking_winget_updates"])
        update_cmd = 'winget upgrade --id Microsoft.Winget --accept-source-agreements --accept-package-agreements'
        output, error, code = self.run_command(update_cmd)
        out_text = output.decode('utf-8', errors='replace').strip()
        err_text = error.decode('utf-8', errors='replace').strip()
        if ("no applicable update found" in out_text.lower() or 
            "no applicable update found" in err_text.lower() or 
            "kein installiertes paket" in out_text.lower() or 
            "kein installiertes paket" in err_text.lower()):
            self.append_log(self.lang["winget_up_to_date"])
        else:
            self.append_log(self.lang["winget_update_output"].format(output=out_text))
        return True

    def start_installation(self):
        """Initiate the installation process."""
        pre_install_command = "echo Pre-installation check running"
        output, error, code = self.run_command(pre_install_command)
        if code != 0:
            errmsg = error.decode('utf-8', errors='replace')
            messagebox.showerror(self.lang["error"], self.lang["pre_install_cmd_fail"].format(errmsg=errmsg))
            self.append_log(self.lang["pre_install_cmd_fail"].format(errmsg=errmsg))
            return
        else:
            outmsg = output.decode('utf-8', errors='replace').strip()
            self.append_log(self.lang["pre_install_check_succeeded"].format(msg=outmsg))
        if not self.check_and_update_winget():
            return
        selected_programs = [program for program, var in zip(self.programs, self.vars) if var.get()]
        if not selected_programs:
            messagebox.showwarning(self.lang["no_selection"], self.lang["select_one"])
            return
        self.cancelled = False
        self.install_button.config(state=ttk.DISABLED)
        self.cancel_button.config(state=ttk.NORMAL)
        self.close_button.config(state=ttk.DISABLED)
        installation_thread = threading.Thread(target=self.install_programs, args=(selected_programs,))
        installation_thread.start()

    def install_programs(self, selected_programs):
        total_count = len(selected_programs)
        failed_programs = []
        for i, program in enumerate(selected_programs):
            if self.cancelled:
                break
            self.queue.put({"type": "status", "message": self.lang["installing"].format(prog=program['name'])})
            num_commands = len(program['command'])
            self.queue.put({"type": "progress_current", "value": 0})
            installed_successfully = True
            for j, cmd in enumerate(program['command']):
                if self.cancelled:
                    break
                output, error, code = self.run_command(cmd)
                if code != 0:
                    error_msg = error.decode("utf-8", errors="replace").strip()
                    if "already installed" in error_msg.lower():
                        self.queue.put({"type": "log", "message": self.lang["already_installed"].format(prog=program['name'])})
                    else:
                        self.queue.put({"type": "log", "message": self.lang["error_installing"].format(prog=program["name"], error=error_msg)})
                        upgrade_cmd = cmd.replace("winget install", "winget upgrade")
                        upgrade_output, upgrade_error, upgrade_code = self.run_command(upgrade_cmd)
                        if upgrade_code != 0:
                            upgrade_error_msg = upgrade_error.decode("utf-8", errors="replace").strip()
                            self.queue.put({"type": "log", "message": self.lang["error_upgrading"].format(prog=program["name"], error=upgrade_error_msg)})
                            installed_successfully = False
                        else:
                            self.queue.put({"type": "log", "message": self.lang["upgraded_successfully"].format(prog=program["name"])})
                    break
                else:
                    output_msg = output.decode("utf-8", errors="replace").strip()
                    if output_msg:
                        self.queue.put({"type": "log", "message": self.lang["output_for"].format(cmd=cmd, output=output_msg)})
                progress_val = ((j + 1) / num_commands) * 100
                self.queue.put({"type": "progress_current", "value": progress_val})
            if not installed_successfully:
                failed_programs.append(program["name"])
            total_progress = ((i + 1) / total_count) * 100
            self.queue.put({"type": "progress_total", "value": total_progress})
        if not self.cancelled:
            if failed_programs:
                failed_str = "\n".join(failed_programs)
                messagebox.showwarning(
                    self.lang["installation_errors"],
                    self.lang["installation_errors_detail"].format(failed=failed_str)
                )
                self.append_log(self.lang["installation_errors_detail"].format(failed=failed_str))
                self.queue.put({"type": "status", "message": self.lang["installation_completed_with_errors"]})
            else:
                self.queue.put({"type": "status", "message": self.lang["installation_completed"]})
                messagebox.showinfo(self.lang["success"], self.lang["installation_success"])
                self.append_log(self.lang["installation_completed"])
        else:
            self.queue.put({"type": "status", "message": self.lang["installation_cancelled"]})
        self.queue.put({"type": "log", "message": self.lang["installation_log_end"]})
        self.root.after(0, lambda: self.install_button.config(state=ttk.NORMAL))
        self.root.after(0, lambda: self.cancel_button.config(state=ttk.DISABLED))
        self.root.after(0, lambda: self.close_button.config(state=ttk.NORMAL))


def is_admin():
    """Check if the current user has administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    """Re-launch the script with administrative privileges."""
    script = os.path.abspath(sys.argv[0] or __file__)
    params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to elevate privileges:\n{str(e)}")
    sys.exit()


# ----------------------------- SILENT MODE HELPERS -----------------------------

def run_command_simple(command: str):
    """Run a command returning (stdout, stderr, returncode)."""
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    return out.decode('utf-8', errors='replace'), err.decode('utf-8', errors='replace'), proc.returncode


def silent_log(msg: str, log_file_path: str):
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(log_file_path, 'a', encoding='utf-8') as f:
            f.write(line + "\n")
    except Exception:
        pass


def build_program_list():
    """Return the same program list used by GUI (duplicated to avoid GUI creation in silent)."""
    return [
        {"name": "DirectX", "command": ["winget install Microsoft.DirectX --force"], "group": "other"},
        {"name": "Java Runtime", "command": ["winget install Oracle.JavaRuntimeEnvironment --force"], "group": "other"},
        {"name": ".Net Runtime 8", "command": ["winget install Microsoft.DotNet.DesktopRuntime.8 --force"], "group": "other"},
        {"name": "OpenAL", "command": ["winget install OpenAL.OpenAL --force"], "group": "other"},
        {"name": "XNA Redist", "command": ["winget install Microsoft.XNARedist --force"], "group": "other"},
        {"name": "VC - Redist 2010", "command": [
            "winget install Microsoft.VCRedist.2010.x64 --force",
            "winget install Microsoft.VCRedist.2010.x86 --force"
        ], "group": "vc"},
        {"name": "VC - Redist 2012", "command": [
            "winget install Microsoft.VCRedist.2012.x64 --force",
            "winget install Microsoft.VCRedist.2012x86 --force"
        ], "group": "vc"},
        {"name": "VC - Redist 2013", "command": [
            "winget install Microsoft.VCRedist.2013.x64 --force",
            "winget install Microsoft.VCRedist.2013.x86 --force"
        ], "group": "vc"},
        {"name": "VC - Redist 2015-2022", "command": [
            "winget install Microsoft.VCRedist.2015+.x64 --force",
            "winget install Microsoft.VCRedist.2015+.x86 --force"
        ], "group": "vc"}
    ]


def add_winget_agreement_flags(cmd: str) -> str:
    # Ensure agreement flags are present for unattended installs
    flags = "--accept-source-agreements --accept-package-agreements"
    if flags in cmd:
        return cmd
    return f"{cmd} {flags}"


def silent_check_winget(log_file: str) -> bool:
    silent_log("Checking winget...", log_file)
    out, err, code = run_command_simple("winget --version")
    if code != 0:
        silent_log("winget not installed. Aborting silent install.", log_file)
        return False
    silent_log(f"winget version: {out.strip()}", log_file)
    up_cmd = "winget upgrade --id Microsoft.Winget --accept-source-agreements --accept-package-agreements"
    uo, ue, _ = run_command_simple(up_cmd)
    lower_combined = (uo + ue).lower()
    if "no applicable update" in lower_combined or "kein installiertes paket" in lower_combined:
        silent_log("winget up to date.", log_file)
    else:
        if uo.strip():
            silent_log("winget upgrade output: " + uo.strip(), log_file)
        if ue.strip():
            silent_log("winget upgrade stderr: " + ue.strip(), log_file)
    return True


def run_silent_install():
    """Perform unattended installation of all predefined runtimes."""
    # Prepare logging
    temp_dir = tempfile.gettempdir()
    work_dir = os.path.join(temp_dir, "universal_runtime_silent")
    os.makedirs(work_dir, exist_ok=True)
    os.chdir(work_dir)
    log_file = os.path.join(work_dir, "installer_log.txt")
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("Universal Runtime Installer Silent Log\n")
    silent_log("Starting silent installation...", log_file)
    if not silent_check_winget(log_file):
        return 1
    programs = build_program_list()
    failed = []
    total = len(programs)
    for idx, prog in enumerate(programs, 1):
        if not isinstance(prog.get('command'), list):
            continue
        silent_log(f"[{idx}/{total}] Installing {prog['name']}...", log_file)
        success = True
        for raw_cmd in prog['command']:
            cmd = add_winget_agreement_flags(raw_cmd)
            out, err, code = run_command_simple(cmd)
            if code != 0:
                # Try upgrade path
                if 'already installed' in (out + err).lower():
                    silent_log(f"{prog['name']} already installed (detected).", log_file)
                    continue
                silent_log(f"Error installing {prog['name']}: {err.strip() or out.strip()} - attempting upgrade.", log_file)
                up_cmd = add_winget_agreement_flags(cmd.replace('winget install', 'winget upgrade'))
                uo, ue, ucode = run_command_simple(up_cmd)
                if ucode != 0:
                    silent_log(f"Upgrade failed for {prog['name']}: {ue.strip() or uo.strip()}", log_file)
                    success = False
                else:
                    silent_log(f"{prog['name']} upgraded successfully.", log_file)
            else:
                if out.strip():
                    silent_log(f"Output: {out.strip().splitlines()[-1]}", log_file)
        if not success:
            failed.append(prog['name'])
        silent_log(f"Progress: {idx}/{total}", log_file)
    if failed:
        silent_log("Completed with errors. Failed: " + ', '.join(failed), log_file)
        return 2
    else:
        silent_log("All installations completed successfully.", log_file)
        return 0


def main():
    try:
        # Argument parsing (simple) for silent mode
        args_lower = [a.lower() for a in sys.argv[1:]]
        silent_requested = any(a in ("/silent", "-silent", "--silent", "/s", "-s") for a in args_lower)

        if silent_requested:
            # Ensure elevation first
            if not is_admin():
                run_as_admin()
                return
            exit_code = run_silent_install()
            sys.exit(exit_code)

        # GUI mode
        if not is_admin():
            run_as_admin()
            return

        temp_dir = tempfile.gettempdir()
        os.chdir(temp_dir)
        temp_cmd_dir = os.path.join(temp_dir, "cmd_temp")
        os.makedirs(temp_cmd_dir, exist_ok=True)
        os.chdir(temp_cmd_dir)
        print("Temporary CMD Working Directory set to:", os.getcwd())
        with open("installer_log.txt", "w", encoding="utf-8") as log_file:
            log_file.write("Installation Log\n")
        root = ttk.Window(themename="flatly")
        root.title("Universal Runtime Installer by Manily - Improved")
        
        icon_file = resource_path("logo.ico")
        try:
            root.iconbitmap(icon_file)
        except Exception as e:
            print("Error setting icon:", e)
        
        app = InstallerGUI(root)
        root.after(100, app.process_queue)
        root.mainloop()
    except Exception:
        error_details = traceback.format_exc()
        messagebox.showerror("Fatal Error", f"An unhandled exception occurred:\n{error_details}")
        print(error_details)
        sys.exit(1)


if __name__ == "__main__":
    main()
