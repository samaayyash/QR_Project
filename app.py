from flask import Flask, render_template, request, jsonify
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import hashlib
import base64
import qrcode
from io import BytesIO
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Fixed encryption key
PASSWORD = b"SecureQR_Project_2026_StrongKey"
salt = b'salt_1234_secure'

# Updated for newer cryptography version
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
)
key = base64.urlsafe_b64encode(kdf.derive(PASSWORD))
cipher = Fernet(key)

def encrypt_data(plain_text):
    """Encrypt data using AES (Fernet)"""
    try:
        encrypted = cipher.encrypt(plain_text.encode('utf-8'))
        return encrypted.decode('utf-8')
    except Exception as e:
        print(f"Encryption error: {e}")
        return None

def decrypt_data(encrypted_text):
    """Decrypt encrypted data"""
    try:
        decrypted = cipher.decrypt(encrypted_text.encode('utf-8'))
        return decrypted.decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {e}")
        return None

def generate_hash(data):
    """Generate SHA-256 hash for integrity verification"""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def generate_qr_code(payload):
    """Generate QR code image as base64 string"""
    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=2,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/secure_qr', methods=['POST'])
def create_secure_qr():
    """Create secure QR code with encryption + hash"""
    data = request.json.get('data', '')
    
    if not data:
        return jsonify({'error': 'Please enter data'}), 400
    
    encrypted_data = encrypt_data(data)
    if not encrypted_data:
        return jsonify({'error': 'Encryption failed'}), 500
    
    original_hash = generate_hash(data)
    
    payload = json.dumps({
        'encrypted': encrypted_data,
        'hash': original_hash
    })
    
    qr_image = generate_qr_code(payload)
    
    return jsonify({
        'success': True,
        'qr_image': qr_image,
        'encrypted_data': encrypted_data,
        'hash': original_hash,
        'original_data': data
    })

@app.route('/api/verify_qr', methods=['POST'])
def verify_qr():
    """Verify QR code and check for tampering"""
    payload = request.json.get('payload', '')
    
    try:
        qr_data = json.loads(payload)
        encrypted_data = qr_data.get('encrypted', '')
        provided_hash = qr_data.get('hash', '')
        
        decrypted_data = decrypt_data(encrypted_data)
        if not decrypted_data:
            return jsonify({
                'success': False,
                'error': 'Decryption failed - Data may be corrupted or wrong key'
            })
        
        computed_hash = generate_hash(decrypted_data)
        
        if computed_hash == provided_hash:
            return jsonify({
                'success': True,
                'verified': True,
                'decrypted_data': decrypted_data,
                'message': '✅ Data is intact and has not been tampered with'
            })
        else:
            return jsonify({
                'success': True,
                'verified': False,
                'error': '⚠️ Tampering detected! Hash mismatch',
                'decrypted_data': decrypted_data
            })
            
    except json.JSONDecodeError:
        return jsonify({
            'success': False,
            'error': 'Invalid QR Code format'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        })

@app.route('/api/tamper_test', methods=['POST'])
def tamper_test():
    """Simulate tampering attack"""
    payload = request.json.get('payload', '')
    
    try:
        qr_data = json.loads(payload)
        original_encrypted = qr_data.get('encrypted', '')
        tampered_encrypted = original_encrypted[:-5] + 'XXXXX'
        qr_data['encrypted'] = tampered_encrypted
        
        tampered_payload = json.dumps(qr_data)
        
        return jsonify({
            'success': True,
            'tampered_payload': tampered_payload
        })
    except:
        return jsonify({'error': 'Failed to simulate tampering'}), 400

@app.route('/api/health', methods=['GET'])
def health():
    """Server health check"""
    return jsonify({'status': 'online', 'crypto': 'AES-128 (Fernet)'})

if __name__ == '__main__':
    print("🚀 Starting Secure QR Server...")
    print("📍 Access at: http://127.0.0.1:5000")
    print("🔐 Encryption System: AES-128 with SHA-256")
    app.run(debug=True, host='0.0.0.0', port=5000)