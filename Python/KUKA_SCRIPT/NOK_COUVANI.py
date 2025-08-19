import os
import re

def extract_ptp_blocks(src_content, stop_line_pattern):
    ptp_blocks = []
    lines = src_content.splitlines()
    block = []
    inside_block = False
    stop_index = None

    for idx, line in enumerate(lines):
        if stop_line_pattern in line:
            stop_index = idx
            break

    for idx, line in enumerate(lines[:stop_index]):
        if line.strip().startswith(";FOLD PTP"):
            block = [line]
            inside_block = True
        elif inside_block:
            block.append(line)
            if line.strip() == ";ENDFOLD":
                ptp_blocks.append("\n".join(block))
                inside_block = False

    return ptp_blocks, stop_index

def modify_src_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    ptp_blocks, insert_index = extract_ptp_blocks(content, "Wait for (Gi_ProgramNumber == 200)")
    if not ptp_blocks or insert_index is None:
        return  # Nothing to modify

    lines = content.splitlines()
    wait_line = lines[insert_index]
    new_wait_line = "Wait for ((Gi_ProgramNumber == 200) OR So_NOK_Part)"
    comment_line = "; Return Home when NOK"

    reversed_moves = "\n".join(reversed(ptp_blocks))
    extra_logic = (
        f"{new_wait_line}\n"
        f"{comment_line}\n"
        f"IF So_NOK_Part == True THEN\n"
        f"{reversed_moves}\n"
        f"  Trigger when distance=1 delay=0 do So_Kriz_Svar_Interlock = True\n"
        f"  SetProgramNumber(999)\n"
        f"  Wait for (Gi_ProgramNumber == 999)\n"
        f"  GOTO KONEC\n"
        f"ENDIF"
    )

    # Insert modification
    lines[insert_index] = extra_logic

    # Add KONEC label before END
    for idx in range(len(lines)):
        if lines[idx].strip() == "END":
            lines.insert(idx, "KONEC:")
            break

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("\n".join(lines))

def process_all_src_files(directory):
    for filename in os.listdir(directory):
        if filename.lower().endswith('.src'):
            filepath = os.path.join(directory, filename)
            print(f"Processing {filepath}...")
            modify_src_file(filepath)

# Example usage
# Replace 'your_directory_path' with the actual path to the folder with .src files
process_all_src_files(r'C:\KRC\Roboter\Program\Svareci_Programy\Profil_TUBE')
