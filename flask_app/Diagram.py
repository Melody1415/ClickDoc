from flask import Flask, request, render_template, session, redirect, url_for
from groq import Groq
import os
import base64
import re
import json

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'yoursecretkey')  # Use env var for security
# Your Groq API key here
GROQ_API_KEY = "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"
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
    
    # Check for common syntax issues
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
        if not re.search(r'\w+\["\w.*"\]', code):  # Check for nodes like main["Main Function"]
            return False
        if not re.search(r'-->\|?.*\|?', code):
            return False
        # CRITICAL: Check for C4 syntax and reject it
        if re.search(r'component\s*\[', code) or re.search(r'as\s+\w+', code):
            return False
    elif diagram_type == 'class':
        if not re.search(r'class\s+\w+', code):
            return False
    return True

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error="No file uploaded!")
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error="No file selected!")
        
        try:
            content_bytes = file.read()
            content = content_bytes.decode('utf-8').strip()
            if not content:
                return render_template('index.html', error="Uploaded file is empty!")
        except UnicodeDecodeError:
            return render_template('index.html', error="Error: File must be text (e.g., .py, .txt, .js, .md, .cpp, .h)!")
        except Exception as e:
            return render_template('index.html', error=f"Error processing file: {str(e)}")
        
        session['file_content'] = base64.b64encode(content_bytes).decode('utf-8')
        session['filename'] = file.filename
        session['regen_count'] = 0  # Initialize regen count
        session['previous_mermaid'] = ''  # Initialize previous Mermaid code
        return redirect(url_for('diagram_page'))
    
    return render_template('index.html', error=None)

@app.route('/diagram', methods=['GET', 'POST'])
def diagram_page():
    if 'file_content' not in session or 'filename' not in session:
        return redirect(url_for('index'))
    
    output_type = request.args.get('output_type', 'flow')

    if request.method == 'POST':
        output_type = request.form.get('output_type', output_type)
        is_regenerate = request.form.get('regenerate') == '1'
        
        try:
            content_bytes = base64.b64decode(session['file_content'])
            content = content_bytes.decode('utf-8').strip()
            if not content:
                return render_template('diagram_page.html', error="Session file is empty!", output_type=output_type, filename=session['filename'], file_content='')
        except Exception as e:
            return render_template('diagram_page.html', error=f"Error decoding session file: {str(e)}", output_type=output_type, filename=session['filename'], file_content='')
        
        # Increment regen count for regeneration
        if is_regenerate:
            session['regen_count'] = session.get('regen_count', 0) + 1
        
        # Build regeneration prompt
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
            temperature = 0.7 if is_regenerate else 0.0  # Higher for regeneration
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
            
            # Clean the response
            ai_response = re.sub(r'```mermaid', '', ai_response)
            ai_response = re.sub(r'```\s*', '', ai_response).strip()
            
            # Auto-fix common syntax errors
            ai_response = re.sub(r'-->(?=\S)', '--> ', ai_response)  # Add missing spaces after arrows
            ai_response = re.sub(r'(\w+)\s+([[{(\["])', r'\1\2', ai_response)  # Remove spaces between node ID and shape/label start
            ai_response = re.sub(r'"\s*([^"]*?)\s*"', r'"\1"', ai_response)  # Trim spaces inside quoted labels
            ai_response = re.sub(r'\("\s*([^"]*?)\s*"\)', r'(\1)', ai_response)  # Simplify labels with nested quotes
            
            if not is_valid_mermaid(ai_response, output_type):
                raise ValueError("Invalid or incomplete Mermaid code generated")
            
            # Store the new Mermaid code for future regenerations
            session['previous_mermaid'] = ai_response
                
        except Exception as e:
            return render_template('diagram_page.html', error=f"API error: {str(e)}", output_type=output_type, filename=session['filename'], file_content=content)
        
        return render_template('generate_page.html', error=None, result=ai_response, filename=session['filename'], output_type=output_type, file_content=content, success="Regeneration successful!" if is_regenerate else None)
    
    try:
        content_bytes = base64.b64decode(session['file_content'])
        content = content_bytes.decode('utf-8').strip()
    except Exception as e:
        return render_template('diagram_page.html', error=f"Error decoding file: {str(e)}", output_type=output_type, filename=session['filename'], file_content='')
    
    return render_template('diagram_page.html', error=None, output_type=output_type, filename=session['filename'], file_content=content)

if __name__ == '__main__':
    app.run(debug=True)