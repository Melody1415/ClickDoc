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

# --------------------------------------------------------------
#  PROMPT TEMPLATES – only the needed part is added to the prompt
# --------------------------------------------------------------
PROMPT_TEMPLATES = {
    'flow': """
- For 'flow': Start with 'flowchart TD'
- EVERY node MUST have an ID: A["Start"], B[Action], C{{Decision}}
- Actions: ID["Do something"]
- Decisions: ID{{condition?}}
- Edges: -->|label|
- End with: End["End"]
- ALWAYS put each node and edge on a SEPARATE line
- NO node without ID
- NO plain ["Label"] without ID
- Example:
  A["Start"] --> B["Print hello"]
  B --> C{{x > 0}}
  C -->|yes| D["Do it"]
  C -->|no| End["End"]
""",

    'component': """
- For 'component': Start with 'flowchart TD'
- EVERY node MUST have ID: Book["Book Class"]
- Use: -->|uses| or -->|calls|
- Subgraphs: subgraph Name["Group Name"]
- End every subgraph with 'end'
- NO C4 syntax
- Example:
  subgraph Book
    B["Book"]
  end
  B -->|uses| Price["Price"]
""",

 'class': """
CRITICAL FOR CLASS DIAGRAMS:
- Start with: classDiagram
- class ClassName{{ +field: type -method(): return }}
- DETECT AND DRAW RELATIONSHIPS:
  * Inheritance: Child --> Parent : extends
  * Composition: Owner "1" --> "1" Part : contains
  * Aggregation: Owner "1" --> "0..*" Part : has
- Use --> for all. Use labels like :extends, :has
- If 'new Class()' → composition
""",

    'sequence': """
- For 'sequence': Start with 'sequenceDiagram'
- participant M as main participant R as Record M->>R: create Record(1, TestRecord) loop while option != 3 M->>M: print "1. Display Record, 2. Process, 3. Exit: " M->>M: input option alt option == 1 M->>R: display() end
- Valid participants, proper arrows (e.g., ->>, -->>), balanced loop/alt.
"""

}

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
        if not code.startswith('classDiagram'):
            return False
        if not re.search(r'class\s+\w+', code):
            return False
        return True
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


               # -----------------------------------------------------------------
        #  DYNAMIC PROMPT – short base + diagram-type specific rules
        # -----------------------------------------------------------------
        base_prompt = f"""
IMPORTANT: OUTPUT ONLY VALID MERMAID CODE FOR '{output_type}'. NO EXPLANATIONS. OUTPUT ONLY CODE.

Follow these rules EXACTLY:

{PROMPT_TEMPLATES.get(output_type, '')}

Code to analyze:
{content}
"""
        prompt = base_prompt
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
    
    # -----------------------------------------------------------------
    #  Use the SAME type-specific rules for “generate all” as in the
    #  single-file view – this guarantees component ≠ class
    # -----------------------------------------------------------------
    base_prompt_template = """
IMPORTANT: OUTPUT ONLY VALID MERMAID CODE FOR '{output_type}'. NO EXPLANATIONS, NO TEXT ANALYSIS, NO EXTRA WORDS, NO COMMENTS. OUTPUT ONLY THE CODE. The code MUST be parseable by Mermaid without errors.

{PROMPT_TEMPLATES}

Code to analyze:
{content}
"""

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
        
        prompt = base_prompt_template.format(
            output_type=output_type,
            PROMPT_TEMPLATES=PROMPT_TEMPLATES.get(output_type, ''),
            content=content
        )
        
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
            
            # ----- normalise code (same as single-file) -----
            ai_response = re.sub(r'```mermaid\s*', '', ai_response, flags=re.DOTALL)
            ai_response = re.sub(r'```\s*', '', ai_response).strip()
            ai_response = re.sub(r'-->(?=\S)', '--> ', ai_response)
            ai_response = re.sub(r'(\w+)\s+([[{(\["])', r'\1\2', ai_response)
            ai_response = re.sub(r'"\s*([^"]*?)\s*"', r'"\1"', ai_response)
            ai_response = re.sub(r'\("\s*([^"]*?)\s*"\)', r'(\1)', ai_response)

            # ----- **FIT TO BOX** – wrap the diagram in a div with fixed size -----
            # (the actual Mermaid rendering is done client-side; we just return the raw code)
            # No extra change needed in Python – the HTML already uses a responsive container.
            # The only thing that helps is guaranteeing **no stray newlines** inside nodes.
            # The regexes above already strip inner spaces, so the diagram stays compact.

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

@diagram.route('/get_diagram/<int:index>', methods=['GET'])
def get_diagram(index):
    all_diagrams = session.get('all_diagrams', [])
    if index < 0 or index >= len(all_diagrams):
        return jsonify({'error': 'Invalid index'}), 400
    diagram_data = all_diagrams[index]
    return jsonify({
        'file_index': diagram_data['file_index'],
        'filename': diagram_data['filename'],
        'diagram': diagram_data['diagram'],
        'error': diagram_data['error']
    })