from app import app
import subprocess
import os
from flask import redirect

# Import the complete DoubleMoney Flask system from original files
from routes import *  # Import all routes from Flask original
from admin_routes import *  # Import admin routes from Flask original

# Laravel DoubleMoney Integration - Direct PHP execution (disabled - using Flask integration)
# @app.route('/doublemoney')
# @app.route('/doublemoney/')
# @app.route('/doublemoney/<path:path>')
def doublemoney_system_disabled(path=''):
    """DoubleMoney Laravel system integrated directly"""
    from flask import request, Response
    import tempfile
    import json
    
    # Create a simple PHP script that executes Laravel
    laravel_dir = os.path.join(os.getcwd(), 'doublemoney-laravel')
    
    if not os.path.exists(laravel_dir):
        return "Laravel system not found", 404
    
    # Create temporary PHP script to handle the request
    request_uri = f'/{path}' if path else '/'
    php_script = f'''<?php
// Set up server environment for Laravel
$_SERVER['REQUEST_METHOD'] = '{request.method}';
$_SERVER['REQUEST_URI'] = '{request_uri}';
$_SERVER['SCRIPT_NAME'] = '/doublemoney/index.php';
$_SERVER['HTTP_HOST'] = 'localhost:5000';
$_SERVER['SERVER_NAME'] = 'localhost';
$_SERVER['SERVER_PORT'] = '5000';
$_SERVER['HTTPS'] = '';
$_SERVER['PATH_INFO'] = '{request_uri}';

// Change to Laravel directory
chdir('{laravel_dir}');

// Bootstrap Laravel application
try {{
    require_once 'vendor/autoload.php';
    $app = require_once 'bootstrap/app.php';
    
    // Create and handle request
    $kernel = $app->make(Illuminate\\Contracts\\Http\\Kernel::class);
    $request = Illuminate\\Http\\Request::capture();
    $response = $kernel->handle($request);
    
    // Output response
    echo $response->getContent();
    $kernel->terminate($request, $response);
}} catch (Exception $e) {{
    // Fallback to direct login page
    echo '<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DoubleMoney - Investment Platform</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        .card {{ background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); }}
    </style>
</head>
<body class="d-flex align-items-center">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card shadow-lg border-0 rounded-4">
                    <div class="card-body p-5">
                        <div class="text-center mb-4">
                            <h1 class="fw-bold text-primary">💰 DoubleMoney</h1>
                            <p class="text-muted">Verdoppeln Sie Ihr Investment in 7 Tagen</p>
                        </div>
                        
                        <div class="alert alert-info">
                            <h5>🚀 Laravel System wird geladen...</h5>
                            <p class="mb-0">Das vollständige DoubleMoney System wird vorbereitet.</p>
                        </div>
                        
                        <div class="row mt-4">
                            <div class="col-6">
                                <h6>✅ Features:</h6>
                                <ul class="small">
                                    <li>Investment-System</li>
                                    <li>Referral-Programm</li>
                                    <li>Admin-Panel</li>
                                </ul>
                            </div>
                            <div class="col-6">
                                <h6>🔐 Admin-Zugang:</h6>
                                <p class="small mb-1"><strong>User:</strong> admin</p>
                                <p class="small"><strong>Pass:</strong> Admin123!"§</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>';
}}
?>'''
    
    # Write and execute PHP script
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
            f.write(php_script)
            f.flush()
            
            result = subprocess.run(['php', f.name], 
                                  capture_output=True, text=True, timeout=30)
            os.unlink(f.name)
            
            if result.returncode == 0:
                content = result.stdout
                # Fix URLs in the content
                content = content.replace('href="/', 'href="/doublemoney/')
                content = content.replace('action="/', 'action="/doublemoney/')
                content = content.replace('src="/', 'src="/doublemoney/')
                return Response(content, content_type='text/html')
            else:
                return f"Laravel Error: {result.stderr}", 500
                
    except Exception as e:
        return f'''
        <html><body style="font-family: Arial; padding: 20px; background: #1e1e1e; color: white;">
        <h1 style="color: #4FC3F7;">DoubleMoney Laravel System</h1>
        <div style="background: #444; padding: 20px; border-radius: 8px;">
            <h2>System wird vorbereitet...</h2>
            <p>Das Laravel DoubleMoney System startet gerade.</p>
            <p><strong>Features:</strong></p>
            <ul>
                <li>Benutzerregistrierung mit Telefonnummer</li>
                <li>Investment-System ($100-$100.000, 7 Tage Verdoppelung)</li>
                <li>5-Tier Referral-System (Bronze bis Diamond)</li>
                <li>Admin-Panel (admin / Admin123!"§)</li>
                <li>Permanente Wallet-Rotation</li>
            </ul>
            <p><em>Aktueller Status: {str(e)}</em></p>
        </div>
        </body></html>
        ''', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
