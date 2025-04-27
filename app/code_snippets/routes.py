"""
Routes for the code snippets blueprint.
"""
from flask import render_template, abort, jsonify
from flask_login import login_required
from app.code_snippets import code_snippets_bp
from app.code_snippets.snippets import get_snippet, get_all_snippets, get_snippets_by_category


@code_snippets_bp.route('/')
@login_required
def index():
    """Display a list of all available code snippets."""
    categorized_snippets = get_snippets_by_category()
    return render_template('code_snippets/index.html',
                          title='Code Examples',
                          categorized_snippets=categorized_snippets)


@code_snippets_bp.route('/category/<category>')
@login_required
def category(category):
    """Display snippets by category."""
    categorized_snippets = get_snippets_by_category()
    
    if category not in categorized_snippets:
        abort(404)
    
    snippets = categorized_snippets[category]
    return render_template('code_snippets/category.html',
                          title=f'Code Examples - {category.replace("_", " ").title()}',
                          category=category,
                          snippets=snippets)


@code_snippets_bp.route('/view/<snippet_id>')
@login_required
def view_snippet(snippet_id):
    """View a specific code snippet."""
    snippet = get_snippet(snippet_id)
    
    if not snippet:
        abort(404)
    
    return render_template('code_snippets/view_snippet.html',
                          title=f'Code Example - {snippet.title}',
                          snippet=snippet)


@code_snippets_bp.route('/api/snippets')
@login_required
def get_snippets_api():
    """API endpoint to get all snippets in JSON format."""
    snippets = get_all_snippets()
    
    # Convert snippets to JSON-serializable format
    snippet_list = []
    for snippet_id, snippet in snippets.items():
        snippet_list.append({
            'id': snippet.id,
            'title': snippet.title,
            'description': snippet.description,
            'language': snippet.language
        })
    
    return jsonify({'snippets': snippet_list})


@code_snippets_bp.route('/api/snippet/<snippet_id>')
@login_required
def get_snippet_api(snippet_id):
    """API endpoint to get a specific snippet in JSON format."""
    snippet = get_snippet(snippet_id)
    
    if not snippet:
        return jsonify({'error': 'Snippet not found'}), 404
    
    snippet_data = {
        'id': snippet.id,
        'title': snippet.title,
        'description': snippet.description,
        'language': snippet.language,
        'code': snippet.code
    }
    
    return jsonify({'snippet': snippet_data})