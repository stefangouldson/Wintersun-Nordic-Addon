"""
Extend all 54-element deity arrays in the Nordic addon TrackerQuest
with a new Stuhn entry (index 54), cloned from Stendarr (index 22).
Modifies the file in-place using text-based insertion to preserve YAML formatting.
"""

TARGET = r"wintersunNordicAddon\Quests\WSN_TrackerQuest_Quest - 005901_Wintersun - Faiths of Skyrim.esp.yaml"
CLONE_INDEX = 22  # Stendarr
CURRENT_SIZE = 54  # arrays currently have 54 elements (0-53)

# Overrides for Stuhn
OVERRIDES = {
    'WSN_DeityName': ['      - Stuhn\n'],
    'WSN_DivineType': ['      - Nordic Deity\n'],
    'WSN_DivineTypeID': ['      - 0\n'],
    'WSN_Blessing': [
        "      - Name: ''\n",
        "        Object: 00081E:WintersunNordicDivines.esp\n",
    ],
    'WSN_FavorDisplay': [
        "      - Name: ''\n",
        "        Object: 000821:WintersunNordicDivines.esp\n",
    ],
    'WSN_Tenet': [
        "      - Name: ''\n",
        "        Object: 000823:WintersunNordicDivines.esp\n",
    ],
    'WSN_Boon1': [
        "      - Name: ''\n",
        "        Object: 000825:WintersunNordicDivines.esp\n",
    ],
    'WSN_Boon2': [
        "      - Name: ''\n",
        "        Object: 000829:WintersunNordicDivines.esp\n",
    ],
}


def find_list_blocks(lines):
    """Find all ListProperty blocks and their per-element line ranges."""
    blocks = []
    i = 0
    while i < len(lines):
        stripped = lines[i].rstrip()
        if 'ListProperty' in stripped and 'MutagenObjectType:' in stripped:
            prop_type = stripped.split('MutagenObjectType:')[1].strip()
            prop_name = ''
            if i + 1 < len(lines) and 'Name:' in lines[i + 1]:
                prop_name = lines[i + 1].split('Name:')[1].strip()

            # Find Data: or Objects: line
            data_line_idx = None
            for j in range(i + 2, min(i + 4, len(lines))):
                sj = lines[j].strip()
                if sj.startswith('Data:') or sj.startswith('Objects:'):
                    data_line_idx = j
                    break

            if data_line_idx is not None:
                elements = parse_elements(lines, data_line_idx + 1)
                if len(elements) == CURRENT_SIZE:
                    blocks.append({
                        'prop_name': prop_name,
                        'prop_type': prop_type,
                        'elements': elements,
                    })
        i += 1
    return blocks


def parse_elements(lines, start):
    """Parse list elements starting at `start`, returning (start, end) line ranges."""
    elements = []
    elem_indent = None
    j = start
    while j < len(lines):
        line = lines[j]
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if stripped.startswith('- '):
            if elem_indent is None:
                elem_indent = indent
            if indent == elem_indent:
                # New element — find its extent
                k = j + 1
                while k < len(lines):
                    sk = lines[k]
                    sk_stripped = sk.lstrip()
                    sk_indent = len(sk) - len(sk_stripped)
                    if sk_stripped == '' or sk_stripped == '\n':
                        k += 1
                    elif sk_stripped.startswith('- ') and sk_indent <= elem_indent:
                        break
                    elif sk_indent <= elem_indent:
                        break
                    else:
                        k += 1
                elements.append((j, k))
                j = k
            elif indent < elem_indent:
                break
            else:
                j += 1
        elif stripped == '' or stripped == '\n':
            j += 1
        elif elem_indent is not None and indent <= elem_indent:
            break
        else:
            j += 1
    return elements


def main():
    with open(TARGET, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    blocks = find_list_blocks(lines)
    print(f"Found {len(blocks)} arrays with 52 elements to extend:")

    # Process in reverse order of position so insertions don't shift later blocks
    blocks.sort(key=lambda b: b['elements'][-1][1], reverse=True)

    for block in blocks:
        name = block['prop_name']
        elems = block['elements']
        insert_pos = elems[-1][1]  # after last element

        if name in OVERRIDES:
            new_lines = OVERRIDES[name]
        else:
            # Clone element at CLONE_INDEX
            src_start, src_end = elems[CLONE_INDEX]
            new_lines = list(lines[src_start:src_end])

        lines[insert_pos:insert_pos] = new_lines
        print(f"  {name}: added Stuhn entry ({len(new_lines)} lines)")

    with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
        f.writelines(lines)

    print(f"\nDone. File now has {len(lines)} lines.")


if __name__ == '__main__':
    main()
