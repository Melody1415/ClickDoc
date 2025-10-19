from flask import Blueprint, request, render_template, session, redirect, url_for, jsonify
from groq import Groq
import os
import re
from dotenv import load_dotenv

diagram = Blueprint('diagram', __name__)

load_dotenv()

# Get API key securely
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing! Please set it in the .env file.")
client = Groq(api_key=GROQ_API_KEY)

# Mermaid syntax validation
def is_valid_mermaid(code, diagram_type):
    if not code:
        return False
    if diagram_type == 'flow' and not code.startswith('flowchart'):
        return False
    if diagram_type == 'sequence' and not code.startswith('sequenceDiagram'):
        return False
    if diagram_type == 'class' and not code.startswith('classDiagram'):
        return False
    if diagram_type == 'component' and not code.startswith('flowchart TD'):
        return False
    
    if diagram_type == 'flow':
        if 'subgraph' in code and code.count('subgraph') != code.count('end'):
            return False
        if not re.search(r'-->\|?.*\|?', code):
            return False
    elif diagram_type == 'sequence':
        if not re.search(r'participant', code) and not re.search(r'actor', code):
            return False
        if not re.search(r'->>|-->>|-->|-\+>|--\+>', code):
            return False
    elif diagram_type == 'component':
        if not re.search(r'\w+\["\w.*"\]', code):
            return False
        if not re.search(r'-->\|?.*\|?', code):
            return False
        if re.search(r'component\s*\[', code) or re.search(r'as\s+\w+', code):
            return False
    elif diagram_type == 'class':
        if not re.search(r'class\s+\w+', code):
            return False
    return True

@diagram.route('/upload_more', methods=['POST'])
def upload_more():
    if 'files' not in request.files:
        return jsonify({'success': False, 'error': 'No files uploaded'}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({'success': False, 'error': 'No valid files provided'}), 400

    allowed_extensions = {
        '.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.c', '.cpp', '.h', '.cs', '.php',
        '.rb', '.go', '.rs', '.swift', '.kt', '.html', '.css', '.json', '.md', '.xml',
        '.yml', '.yaml', '.properties', '.sh', '.bash', '.sql', '.r', '.scala', '.dart'
    }

    valid_files = []
    invalid_files = []

    for file in files:
        if file.filename == '':
            continue
        ext = '.' + file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        if ext in allowed_extensions:
            valid_files.append(file)
        else:
            invalid_files.append(file.filename)

    if not valid_files:
        return jsonify({
            'success': False,
            'error': f'No valid files uploaded. Invalid files: {", ".join(invalid_files)}'
        }), 400

    # Get existing files from session
    session_files = session.get('files', [])

    # Update session files, overwriting duplicates by name
    for file in valid_files:
        content = file.read().decode('utf-8', errors='ignore')  # Decode with error handling
        file_data = {
            'name': file.filename,
            'content': content,
            'size': len(content.encode('utf-8'))  # Approximate size in bytes
        }
        # Check for existing file with same name
        existing_index = next((i for i, f in enumerate(session_files) if f['name'] == file.filename), None)
        if existing_index is not None:
            session_files[existing_index] = file_data
        else:
            session_files.append(file_data)

    session['files'] = session_files

    # Prepare response with file metadata (no content)
    uploaded_files = [{'name': f['name'], 'size': f['size']} for f in session_files]

    return jsonify({
        'success': True,
        'uploaded_files': uploaded_files
    })

@diagram.route('/diagram_page', methods=['GET', 'POST'])
def diagram_page():
    # Initialize session['files'] if not exists
    if 'files' not in session:
        session['files'] = []
    
    # Check for session['files'] or convert session['file'] to session['files']
    files = session.get('files', [])
    if not files and 'file' in session:
        file_dict = session['file']
        if file_dict:
            filename, content = next(iter(file_dict.items()))
            files = [{'name': filename, 'content': content, 'size': len(content.encode('utf-8'))}]
            session['files'] = files
            session.pop('file', None)  # Clean up session['file']
    
    # Create indexed_files for template
    indexed_files = [{'index': i, 'name': f.get('name', 'Unknown'), 'content': f.get('content', '')} for i, f in enumerate(files)]

    # Set default file_index to 0 if files exist, otherwise -1
    if files:
        file_index = request.args.get('file_index', 0, type=int)  # Default to 0 for GET
        if request.method == 'POST':
            file_index = int(request.form.get('file_index', 0))
        # Validate file_index
        if file_index < 0 or file_index >= len(files):
            file_index = 0  # Default to first file
        selected_file = files[file_index]
    else:
        file_index = -1  # No files available
        selected_file = None

    output_type = request.args.get('output_type', 'flow')
    if request.method == 'POST':
        output_type = request.form.get('output_type', output_type)
        is_regenerate = request.form.get('regenerate') == '1'

        # Only proceed with diagram generation if explicitly triggered
        if not files or file_index == -1:
            return render_template('diagram_page.html', error="No valid file selected!", indexed_files=indexed_files, file_index=file_index, output_type=output_type)

        if is_regenerate:
            session['regen_count'] = session.get('regen_count', 0) + 1

        prompt_extra = ""
        if is_regenerate:
            prompt_extra = f"""
This is a regeneration request. Review the previous structure and improve it: 
- Fix any potential syntax errors in the Mermaid code.
- Add more details to nodes/edges if missing (e.g., include function parameters or I/O operations).
- Provide an alternative representation if possible (e.g., different grouping in subgraphs or clearer labels).
- Avoid repeating the same structure exactly.
Previous Mermaid code (if available): {session.get('previous_mermaid', 'None')}
"""
            if session.get('regen_count', 0) > 2:
                prompt_extra += "\nMultiple regenerations detected—simplify the diagram: reduce nodes, focus on high-level structure."

        # Get file content for the selected file
        selected_file = files[file_index]
        content = selected_file.get('content', '').strip()
        if not content:
            return render_template('diagram_page.html', error="Selected file is empty!", indexed_files=indexed_files, file_index=file_index, output_type=output_type)

        prompt = f"""
IMPORTANT: OUTPUT ONLY VALID MERMAID CODE FOR '{output_type}'. NO EXPLANATIONS, NO TEXT ANALYSIS, NO EXTRA WORDS, NO COMMENTS. OUTPUT ONLY THE CODE. The code MUST be parseable by Mermaid without errors.

Analyze the code to identify its structures: functions, classes, methods, loops, conditionals, and interactions (e.g., function calls, object creation, I/O operations). Generate Mermaid code that accurately represents the code's structure for '{output_type}'.

Rules (STRICTLY FOLLOW THESE TO AVOID PARSE ERRORS):
- For 'flow': Start with 'flowchart TD'. Use [] for actions, {{}} for decisions, -->|label| for edges (no quotes in labels). Include all control flow paths (if-else, while loops) with backward edges for loops. Include I/O operations (e.g., print, input) as nodes. End with an 'End' node.
- Node labels: Use plain text for simple labels. For ANY label with spaces, special characters (e.g., (, ), ,, :, /, <, >), or details, ALWAYS enclose the ENTIRE label in double quotes inside the shape, e.g., ["Print message"], ["Input option"], ["Create Record(1, TestRecord)"]. If inner double quotes are absolutely needed, escape them as \", e.g., ["Print \"message\""], but STRICTLY prefer simplifying by removing unnecessary inner quotes or rephrasing (e.g., use TestRecord without quotes). This prevents parse errors from unbalanced or special characters.
- ALWAYS output each node and edge on a SEPARATE NEW LINE to ensure proper separation and avoid concatenated tokens (e.g., do NOT output ]C; use a newline after each statement). Ensure spaces around elements where needed (e.g., after action words inside labels: ["Print message"] NOT ["Printmessage"]).
- Include all control flow: Use backward edges (e.g., H --> D) for loops. For conditionals, branch from decision nodes with ALL paths (e.g., |yes|, |no|; or |1|, |2|, |else| for multi-way). End with a rectangular [End] node.
- I/O operations: Represent as action nodes (e.g., ["Print message"], ["Input option"]).
- Common pitfalls to AVOID: NO extra spaces after closing ] or }}. NO missing spaces in labels (e.g., Print"message" is INVALID; use "Print message"). NO quotes in edge labels. Ensure balanced branches—no misplaced edges from non-decision nodes. NO special characters in labels without double-quoting the entire label.
- Self-validate: After generating, mentally check: Are all complex labels enclosed in double quotes inside shapes (e.g., ["label with (parens)"])? Are inner quotes escaped or avoided? Is each statement on its own line? Are edges simple (-->|label| with no quotes)? Does it match the example structure? If not, adjust to ensure it parses without errors like unexpected tokens.

Examples:
- Flow: flowchart TD A[Start] --> B[main] --> B1[Create Record(1, "TestRecord")] --> C{{option != 3}} -->|yes| D[Print "1. Display Record, 2. Process, 3. Exit: "] D --> E[Input option] E --> F{{option?}} F -->|1| G[record.display()] G --> C F -->|3| I[Print "Program ended"] I --> End
- Sequence: sequenceDiagram participant M as main participant R as Record M->>R: create Record(1, TestRecord) loop while option != 3 M->>M: print "1. Display Record, 2. Process, 3. Exit: " M->>M: input option alt option == 1 M->>R: display() end
- Class: classDiagram class Record{{+int id +string name +Record(int, string) +display()}}
- Component: flowchart TD subgraph Program main["Main Function"] -->|uses| Record["Record Class"] main -->|calls| processData["Process Data Function"] end main -->|uses| std_cout["std::cout"] main -->|uses| std_cin["std::cin"] Record -->|uses| std_cout processData -->|uses| std_cout

Ensure syntax is valid for '{output_type}':
- Flow: Balanced branches, valid edges (-->|label| with no quotes or spaces in label), no spaces between ID and shape, proper spacing in node labels (e.g., Print "text"), simple labels without nested quotes. MUST render without parse errors.
- Sequence: Valid participants, proper arrows (e.g., ->>, -->>), balanced loop/alt.
- Class: Correct class syntax, no invalid tags.
- Component: Use [alias]["label"], directed arrows (-->|label|), optional subgraphs. NO C4 SYNTAX. No spaces between ID and [.

Match the code's structure exactly. For loops, use backward edges. For conditionals, include all branches. For interactions, capture function calls, object creation, and I/O.

{prompt_extra}

Code to analyze:\n\n{content}
"""
        try:
            temperature = 0.7 if is_regenerate else 0.0
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful code documentation assistant. For component diagrams, use ONLY standard Mermaid flowchart syntax. NEVER use C4 PlantUML syntax like 'component [name] as label'."
                    },
                    {"role": "user", "content": prompt},
                ],
                model="llama-3.3-70b-versatile",
                max_tokens=2000,
                temperature=temperature
            )
            ai_response = chat_completion.choices[0].message.content.strip()

            ai_response = re.sub(r'```mermaid', '', ai_response)
            ai_response = re.sub(r'```\s*', '', ai_response).strip()

            ai_response = re.sub(r'-->(?=\S)', '--> ', ai_response)
            ai_response = re.sub(r'(\w+)\s+([[{(\["])', r'\1\2', ai_response)
            ai_response = re.sub(r'"\s*([^"]*?)\s*"', r'"\1"', ai_response)
            ai_response = re.sub(r'\("\s*([^"]*?)\s*"\)', r'(\1)', ai_response)

            if not is_valid_mermaid(ai_response, output_type):
                raise ValueError("Invalid or incomplete Mermaid code generated")

            session['previous_mermaid'] = ai_response

        except Exception as e:
            return render_template('diagram_page.html', error=f"API error: {str(e)}", indexed_files=indexed_files, file_index=file_index, output_type=output_type)

        return render_template('generate_page.html', result=ai_response, indexed_files=indexed_files, file_index=file_index, output_type=output_type, error=None)


    indexed_files = [{'index': i, 'name': f.get('name', 'Unknown'), 'content': f.get('content', '')} for i, f in enumerate(files)]

    # Only try to read file content if files exist and file_index is valid
    content = ''
    if files and file_index >= 0:
        selected_file = files[file_index]
        try:
            filename = selected_file.get('name', 'Unknown')
            content = selected_file.get('content', '').strip()
            if not content:
                return render_template('diagram_page.html', error="Selected file is empty!", indexed_files=indexed_files, file_index=file_index, output_type=output_type)
        except Exception as e:
            return render_template('diagram_page.html', error=f"Error reading file: {str(e)}", indexed_files=indexed_files, file_index=file_index, output_type=output_type)

    return render_template('diagram_page.html', error=None, indexed_files=indexed_files, file_index=file_index, output_type=output_type, file_content=content)

@diagram.route('/generate_all', methods=['POST'])
def generate_all():
    files = session.get('files', [])
    if not files or len(files) == 0:
        return jsonify({'error': 'No files available'}), 400
    
    output_type = request.form.get('output_type', 'flow')
    all_diagrams = []
    
    for index, file_data in enumerate(files):
        content = file_data.get('content', '').strip()
        if not content:
            all_diagrams.append({
                'file_index': index,
                'filename': file_data.get('name', 'Unknown'),
                'error': 'File is empty',
                'diagram': None
            })
            continue
        
        prompt = f"""
IMPORTANT: OUTPUT ONLY VALID MERMAID CODE FOR '{output_type}'. NO EXPLANATIONS, NO TEXT ANALYSIS, NO EXTRA WORDS, NO COMMENTS. OUTPUT ONLY THE CODE. The code MUST be parseable by Mermaid without errors.

Analyze the code to identify its structures: functions, classes, methods, loops, conditionals, and interactions (e.g., function calls, object creation, I/O operations). Generate Mermaid code that accurately represents the code's structure for '{output_type}'.

Rules (STRICTLY FOLLOW THESE TO AVOID PARSE ERRORS):
- For 'flow': Start with 'flowchart TD'. Use [] for actions, {{}} for decisions, -->|label| for edges (no quotes in labels). Include all control flow paths (if-else, while loops) with backward edges for loops. Include I/O operations (e.g., print, input) as nodes. End with an 'End' node.
- Node labels: Use plain text for simple labels. For ANY label with spaces, special characters (e.g., (, ), ,, :, /, <, >), or details, ALWAYS enclose the ENTIRE label in double quotes inside the shape, e.g., ["Print message"], ["Input option"], ["Create Record(1, TestRecord)"]. If inner double quotes are absolutely needed, escape them as \", e.g., ["Print \"message\""], but STRICTLY prefer simplifying by removing unnecessary inner quotes or rephrasing (e.g., use TestRecord without quotes). This prevents parse errors from unbalanced or special characters.
- ALWAYS output each node and edge on a SEPARATE NEW LINE to ensure proper separation and avoid concatenated tokens (e.g., do NOT output ]C; use a newline after each statement). Ensure spaces around elements where needed (e.g., after action words inside labels: ["Print message"] NOT ["Printmessage"]).

Code to analyze:\n\n{content}
"""
        
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful code documentation assistant. For component diagrams, use ONLY standard Mermaid flowchart syntax. NEVER use C4 PlantUML syntax like 'component [name] as label'."
                    },
                    {"role": "user", "content": prompt},
                ],
                model="llama-3.3-70b-versatile",
                max_tokens=2000,
                temperature=0.0
            )
            ai_response = chat_completion.choices[0].message.content.strip()
            
            ai_response = re.sub(r'```mermaid\s*', '', ai_response, flags=re.DOTALL)
            ai_response = re.sub(r'```\s*', '', ai_response).strip()
            ai_response = re.sub(r'-->(?=\S)', '--> ', ai_response)
            ai_response = re.sub(r'(\w+)\s+([[{(\["])', r'\1\2', ai_response)
            ai_response = re.sub(r'"\s*([^"]*?)\s*"', r'"\1"', ai_response)
            ai_response = re.sub(r'\("\s*([^"]*?)\s*"\)', r'(\1)', ai_response)
            
            all_diagrams.append({
                'file_index': index,
                'filename': file_data.get('name', 'Unknown'),
                'diagram': ai_response,
                'error': None
            })
        except Exception as e:
            all_diagrams.append({
                'file_index': index,
                'filename': file_data.get('name', 'Unknown'),
                'error': str(e),
                'diagram': None
            })
    
    session['all_diagrams'] = all_diagrams
    session['current_diagram_index'] = 0
    return jsonify({'success': True, 'total': len(all_diagrams)})