import base64, io

from flask import Flask, render_template, request, redirect, url_for, session
from PIL import Image
import os



# Flask ko batana ke templates aur static folders bahar root par hain
app = Flask(__name__, 
            template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../templates')),
            static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../static')))

app.secret_key = "my_secret_key"

user_data = {
    "user_ip": [],
    "email": [],
    "username": [],
    "password": []
}



@app.route('/', methods=['GET', 'POST'])
def home():
    user = None

    user_ip = request.remote_addr
    user = user_ip in user_data['user_ip']
    username = session.get('user') if user else None
    email = session.get('email') if user else None


    return render_template('index.html', user=user, username=username, email=email)

# this tool route
@app.route('/tool', methods=['GET', 'POST'])
def tool():
    encoded_image = None  # Yeh HTML ko pass hoga
    user = None

    user_ip = request.remote_addr
    user = user_ip in user_data['user_ip']
    username = session.get('user') if user else None
    email = session.get('email') if user else None


    if request.method == 'POST':
        # 1. HTML se photo received ki (using input's name attribute)
        file = request.files.get('my_photo')
        ext = request.form.get('format')

        if file and file.filename != '':
            # 2. Pillow library se image ko open kiya (Processing)
            img = Image.open(file.stream)
            
            # [Optional] Yahan aap image par koi bhi operation kar sakte hain (e.g., resize, filter)
            # img = img.convert('L') # Udaharan ke liye: Image ko Black & White karna
            
            # 3. Image ko memory buffer me save karke Base64 string banaya
            buffer = io.BytesIO()
            img.save(buffer, format=ext.upper() if ext in ['png', 'jpg', 'webp', 'avif'] else 'PNG')
            b64_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Data URL format jo HTML ka <img> tag samajhta hai
            encoded_image = f"data:image/{ext};base64,{b64_string}"            

            
    return render_template('tool.html', user_photo=encoded_image, user_ip=user_ip, user=user, username=username, email=email)



@app.route('/compressor', methods=['GET', 'POST'])
def compressor():
    encoded_image = None  # Yeh HTML ko pass hoga
    user = None

    user_ip = request.remote_addr
    user = user_ip in user_data['user_ip']
    username = session.get('user') if user else None
    email = session.get('email') if user else None


    if request.method == 'POST':
        quality = request.form.get('quality')
        file = request.files.get('my_photo')
        format = file.filename.split('.')[-1].lower()

        img = Image.open(file.stream)

        buffer = io.BytesIO()
        img.save(buffer, format=format.upper() if format in ['png', 'jpg', 'webp', 'avif'] else 'PNG', quality=int(quality), optimize=True)
        b64_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Data URL format jo HTML ka <img> tag samajhta hai
        encoded_image = f"data:image/{format};base64,{b64_string}"

    return render_template('compressor.html', compressed_photo=encoded_image, user=user, username=username, email=email)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in user_data['username'] and password in user_data['password']:
            # session['user'] = username
            # session['pass'] = password
            return redirect('/')
        else:
            return redirect(url_for('signup'))
        
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user_ip = request.remote_addr
        session['user'] = username
        session['email'] = email
        session['user_ip'] = user_ip
        session['pass'] = password
        if email not in user_data['email']:
            user_data['username'].append(username)
            user_data['email'].append(email)
            user_data['password'].append(password)
            user_data['user_ip'].append(user_ip)
            return redirect('/')
        else:
            return redirect(url_for('login'))
    
    return render_template('signup.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)