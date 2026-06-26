"""
Buy, Borrow, Die Calculator - Web Server
=========================================

A minimal Flask server that:
    1. Serves the frontend HTML page
    2. Provides a JSON API endpoint for calculations

The financial calculations are handled by calculator.py (auditable Python code).
The frontend handles all visualization and user interaction.

Usage:
    python app.py
    
    Then open http://localhost:5000 in your browser.

Dependencies:
    pip install flask

Author: Generated for auditing purposes
License: Public Domain
"""

from flask import Flask, request, jsonify, send_from_directory
import calculator

app = Flask(__name__, static_folder='static')


@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_from_directory('.', 'index.html')


@app.route('/api/calculate', methods=['POST'])
def api_calculate():
    """
    API endpoint for running the simulation.
    
    Expects JSON body:
    {
        "initial_investment": 5000000,
        "annual_borrowing": 200000,
        "investment_growth": 8,      // percentage (will be converted to decimal)
        "loan_interest": 5,          // percentage
        "inflation": 3,              // percentage
        "max_leverage": 50,          // percentage
        "years": 30
    }
    
    Returns JSON:
    {
        "success": true,
        "data": {
            "summary": { ... },
            "years": [ ... ]
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No JSON data provided"}), 400
        
        # Extract and validate parameters
        # Frontend sends percentages (e.g., 8 for 8%), convert to decimals (0.08)
        initial_investment = float(data.get('initial_investment', 0))
        annual_borrowing = float(data.get('annual_borrowing', 0))
        investment_growth = float(data.get('investment_growth', 0)) / 100.0
        loan_interest = float(data.get('loan_interest', 0)) / 100.0
        inflation = float(data.get('inflation', 0)) / 100.0
        max_leverage = float(data.get('max_leverage', 50)) / 100.0
        num_years = int(data.get('years', 30))
        
        # Run the simulation (this calls the auditable Python code)
        result = calculator.simulate(
            initial_investment=initial_investment,
            annual_borrowing=annual_borrowing,
            investment_growth=investment_growth,
            loan_interest=loan_interest,
            inflation=inflation,
            max_leverage=max_leverage,
            num_years=num_years
        )
        
        # Convert to JSON-serializable format
        result_dict = calculator.to_dict(result)
        
        return jsonify({
            "success": True,
            "data": result_dict
        })
        
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "ok", "service": "bbd-calculator"})


if __name__ == '__main__':
    print("=" * 60)
    print("Buy, Borrow, Die Calculator")
    print("=" * 60)
    print("Starting server at http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
