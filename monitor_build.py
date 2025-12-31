#!/usr/bin/env python3
"""Docker Build Progress Monitor with Visual Progress Bar"""

import sys
import time
import os
from datetime import datetime, timedelta

# ANSI color codes
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'

def progress_bar(current, total, width=50, label=""):
    """Create a visual progress bar"""
    filled = int(width * current / total)
    bar = '█' * filled + '░' * (width - filled)
    percent = (current / total) * 100
    return f"{label}: [{bar}] {percent:6.2f}%"

def format_time(seconds):
    """Format seconds to human-readable time"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds/60)}m {int(seconds%60)}s"
    else:
        return f"{int(seconds/3600)}h {int((seconds%3600)/60)}m"

def monitor_build(log_file):
    """Monitor Docker build progress"""

    # Build steps with estimated times (in seconds)
    steps = [
        {"name": "Load build context", "estimate": 20, "current": 0, "total": 1},
        {"name": "Install gcc/g++ (71.3 MB)", "estimate": 900, "current": 0, "total": 41},  # 15 min
        {"name": "Setup working directory", "estimate": 10, "current": 0, "total": 1},
        {"name": "Copy requirements.txt", "estimate": 5, "current": 0, "total": 1},
        {"name": "Install PyTorch CPU (184.5 MB)", "estimate": 1600, "current": 0, "total": 1},  # 25 min
        {"name": "Install Python packages (~60 MB)", "estimate": 800, "current": 0, "total": 50},  # 13 min
        {"name": "Compile hdbscan", "estimate": 600, "current": 0, "total": 1},  # 10 min
        {"name": "Copy application code", "estimate": 10, "current": 0, "total": 1},
        {"name": "Create logs directory", "estimate": 5, "current": 0, "total": 1},
        {"name": "Finalize image", "estimate": 20, "current": 0, "total": 1}
    ]

    current_step = 0
    start_time = time.time()
    last_size = 0

    print(f"\n{BOLD}{CYAN}╔══════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║     Docker Build Progress Monitor - Strategic Insight Engine    ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════════════╝{RESET}\n")

    while True:
        try:
            if not os.path.exists(log_file):
                print(f"{YELLOW}Waiting for build to start...{RESET}")
                time.sleep(2)
                continue

            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            current_size = len(content)
            if current_size == last_size:
                # No new data, but might be processing
                time.sleep(1)
                continue

            last_size = current_size
            lines = content.split('\n')

            # Parse current progress
            for line in lines:
                # Step 1: gcc installation
                if 'Unpacking' in line and 'amd64.deb' in line:
                    # Extract package number
                    if current_step < 1:
                        current_step = 1
                    steps[1]["current"] = min(steps[1]["current"] + 1, steps[1]["total"])

                elif 'Setting up' in line and current_step == 1:
                    steps[1]["current"] = min(steps[1]["current"] + 1, steps[1]["total"])

                # Step 2: PyTorch
                elif 'Installing collected packages' in line and 'torch' in line:
                    if current_step < 4:
                        current_step = 4
                        steps[1]["current"] = steps[1]["total"]  # gcc done
                        steps[2]["current"] = steps[2]["total"]  # workdir done
                        steps[3]["current"] = steps[3]["total"]  # copy done

                elif 'Successfully installed' in line and 'torch' in line:
                    steps[4]["current"] = steps[4]["total"]
                    if current_step < 5:
                        current_step = 5

                # Step 3: Python packages
                elif 'Downloading' in line and current_step >= 5:
                    steps[5]["current"] = min(steps[5]["current"] + 1, steps[5]["total"])

                # Step 4: hdbscan compilation
                elif 'Building wheel for hdbscan' in line:
                    if current_step < 6:
                        current_step = 6
                        steps[5]["current"] = steps[5]["total"]

                elif 'still running' in line and 'hdbscan' in line:
                    steps[6]["current"] = min(steps[6]["current"] + 0.2, 0.9)

                elif 'Successfully installed' in line and 'hdbscan' in line:
                    steps[6]["current"] = steps[6]["total"]
                    if current_step < 7:
                        current_step = 7

                # Completion
                elif 'Successfully built' in line or 'Successfully tagged' in line:
                    for i in range(len(steps)):
                        steps[i]["current"] = steps[i]["total"]
                    current_step = len(steps) - 1

            # Calculate overall progress
            total_estimate = sum(s["estimate"] for s in steps)
            completed_time = sum(steps[i]["estimate"] for i in range(current_step))

            if current_step < len(steps) and steps[current_step]["total"] > 0:
                step_progress = steps[current_step]["current"] / steps[current_step]["total"]
                completed_time += steps[current_step]["estimate"] * step_progress

            overall_progress = (completed_time / total_estimate) * 100

            # Calculate time
            elapsed = time.time() - start_time
            if overall_progress > 5:
                estimated_total = (elapsed / overall_progress) * 100
                remaining = estimated_total - elapsed
            else:
                remaining = total_estimate - completed_time

            # Clear screen and display
            os.system('cls' if os.name == 'nt' else 'clear')

            print(f"\n{BOLD}{CYAN}╔══════════════════════════════════════════════════════════════════╗{RESET}")
            print(f"{BOLD}{CYAN}║     Docker Build Progress Monitor - Strategic Insight Engine    ║{RESET}")
            print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════════════╝{RESET}\n")

            # Overall progress
            print(f"{BOLD}Overall Progress:{RESET}")
            print(progress_bar(overall_progress, 100, 60, "  ") + f" {overall_progress:.1f}%")
            print(f"\n{BOLD}Time:{RESET} Elapsed: {GREEN}{format_time(elapsed)}{RESET} | "
                  f"Remaining: {YELLOW}{format_time(remaining)}{RESET}\n")

            # Individual steps
            print(f"{BOLD}Build Steps:{RESET}\n")
            for i, step in enumerate(steps):
                if i < current_step:
                    status = f"{GREEN}✓ DONE{RESET}"
                    bar = progress_bar(step["total"], step["total"], 40, "")
                elif i == current_step:
                    status = f"{YELLOW}⟳ RUNNING{RESET}"
                    bar = progress_bar(step["current"], step["total"], 40, "")
                else:
                    status = f"{CYAN}⋯ PENDING{RESET}"
                    bar = progress_bar(0, step["total"], 40, "")

                print(f"  {i+1}. {step['name']:<40} {status}")
                print(f"     {bar}")

            print(f"\n{CYAN}{'─' * 68}{RESET}")
            print(f"{BOLD}Current Activity:{RESET}")
            if current_step < len(steps):
                print(f"  {YELLOW}▸{RESET} {steps[current_step]['name']}")
            else:
                print(f"  {GREEN}✓{RESET} Build complete!")

            time.sleep(2)

        except KeyboardInterrupt:
            print(f"\n{YELLOW}Monitoring stopped.{RESET}")
            break
        except Exception as e:
            print(f"{RED}Error: {e}{RESET}")
            time.sleep(2)

if __name__ == "__main__":
    log_file = r"C:\Users\DELL\AppData\Local\Temp\claude\C--Users-DELL-Documents-n8n-strategic-insight-engine\tasks\b008ba2.output"

    if len(sys.argv) > 1:
        log_file = sys.argv[1]

    monitor_build(log_file)
