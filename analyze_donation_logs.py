#!/usr/bin/env python3
"""
Donation Log Analyzer
Parse and analyze donation-related logs to identify issues and flow
"""

import os
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime


def analyze_logs(log_dir: str = "logs"):
    """Analyze all logs for donation-related messages"""
    
    if not os.path.exists(log_dir):
        print(f"Log directory not found: {log_dir}")
        return
    
    print("\n" + "="*80)
    print("DONATION SYSTEM LOG ANALYZER")
    print("="*80)
    
    log_files = sorted(Path(log_dir).glob("*.log"), key=os.path.getctime, reverse=True)
    
    if not log_files:
        print("No log files found in logs/ directory")
        return
    
    latest_log = log_files[0]
    print(f"\nAnalyzing: {latest_log.name}\n")
    
    donation_flows = []
    current_flow = []
    api_calls = []
    errors = []
    detections = defaultdict(int)
    
    with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if '[DONATION' in line or '[DONATION FLOW' in line or '[DONATION API' in line:
                
                if '[ERROR' in line or '[DONATION ERROR' in line:
                    errors.append(line.strip())
                
                if '[DONATION FLOW]' in line:
                    if current_flow:
                        donation_flows.append(current_flow)
                    current_flow = [line.strip()]
                elif '[DONATION]' in line and 'FLOW' not in line:
                    current_flow.append(line.strip())
                    
                    if 'Clan chat presence:' in line:
                        if 'YES' in line:
                            detections['clan_chat_found'] += 1
                        else:
                            detections['clan_chat_not_found'] += 1
                    elif 'Troop scan result:' in line:
                        detections['troop_scan'] += 1
                    elif 'Spell scan result:' in line:
                        detections['spell_scan'] += 1
                    elif 'Donate button found' in line:
                        detections['donate_button_found'] += 1
                    elif 'Donate button not found' in line:
                        detections['donate_button_not_found'] += 1
                
                if '[DONATION API]' in line:
                    api_calls.append(line.strip())
    
    if current_flow:
        donation_flows.append(current_flow)
    
    print("📊 SUMMARY STATISTICS")
    print("-" * 80)
    print(f"Total donation detection cycles: {len(donation_flows)}")
    print(f"Total API calls: {len(api_calls)}")
    print(f"Total errors: {len(errors)}")
    
    print("\n📈 DETECTION RESULTS")
    print("-" * 80)
    for detection_type, count in sorted(detections.items()):
        print(f"  • {detection_type}: {count}")
    
    if errors:
        print("\n❌ ERRORS FOUND")
        print("-" * 80)
        for i, error in enumerate(errors[-10:], 1):
            print(f"  {i}. {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
    else:
        print("\n✓ NO ERRORS FOUND")
    
    print("\n📝 RECENT DONATION FLOWS")
    print("-" * 80)
    
    for idx, flow in enumerate(donation_flows[-3:], 1):
        print(f"\nFlow #{len(donation_flows) - (3 - idx)}:")
        for line in flow[:15]:
            timestamp = extract_timestamp(line)
            message = extract_message(line)
            indent = "  " if "[DONATION FLOW]" not in line else ""
            print(f"{indent}• {message}")
        if len(flow) > 15:
            print(f"  ... ({len(flow) - 15} more lines)")
    
    print("\n" + "="*80)
    print("API CALL SEQUENCE (Last 20)")
    print("-" * 80)
    for call in api_calls[-20:]:
        print(f"  • {extract_message(call)}")
    
    print("\n" + "="*80)
    print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Full log: {latest_log}")
    print("="*80 + "\n")


def extract_timestamp(line: str) -> str:
    """Extract timestamp from log line"""
    parts = line.split(' - ')
    if len(parts) > 0:
        return parts[0].strip()
    return ""


def extract_message(line: str) -> str:
    """Extract just the message part from log line"""
    parts = line.split(' - ')
    if len(parts) >= 3:
        return ' - '.join(parts[2:]).strip()
    elif len(parts) >= 2:
        return parts[1].strip()
    return line.strip()


def interactive_mode():
    """Interactive mode to browse logs"""
    print("\n" + "="*80)
    print("INTERACTIVE LOG BROWSER")
    print("="*80)
    
    log_dir = "logs"
    if not os.path.exists(log_dir):
        print(f"Log directory not found: {log_dir}")
        return
    
    log_files = sorted(Path(log_dir).glob("*.log"), key=os.path.getctime, reverse=True)
    
    if not log_files:
        print("No log files found")
        return
    
    print("\nAvailable log files:")
    for i, log_file in enumerate(log_files[:10], 1):
        mod_time = datetime.fromtimestamp(os.path.getmtime(log_file))
        print(f"  {i}. {log_file.name} ({mod_time.strftime('%Y-%m-%d %H:%M')})")
    
    choice = input("\nSelect log file (1-10) or 'q' to quit: ").strip()
    
    if choice.lower() == 'q':
        return
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(log_files):
            selected_log = log_files[idx]
            search_term = input("Search for term (e.g., 'DONATION', 'ERROR', 'troop'): ").strip()
            
            print(f"\nSearching '{search_term}' in {selected_log.name}:\n")
            
            count = 0
            with open(selected_log, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if search_term.upper() in line.upper():
                        print(line.rstrip())
                        count += 1
                        if count >= 50:
                            print(f"\n... (showing first 50 matches, total: {sum(1 for _ in open(selected_log) if search_term.upper() in _.upper())})")
                            break
            
            if count == 0:
                print(f"No matches found for '{search_term}'")
    except (ValueError, IndexError):
        print("Invalid selection")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "interactive":
        interactive_mode()
    else:
        analyze_logs()
