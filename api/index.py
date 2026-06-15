from email.mime import image
import base64, io
from supabase import create_client, Client
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, session
from PIL import Image, ImageEnhance
import os
from dotenv import load_dotenv

load_dotenv()
# Flask ko batana ke templates aur static folders bahar root par hain
app = Flask(__name__, 
            template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../templates')),
            static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../static')))

url: str = os.getenv("URL")
key: str = os.getenv("KEY")
supabase: Client = create_client(url, key)


app.secret_key = "my_secret_key"

user_ip = [

    ]


@app.route('/', methods=['GET', 'POST'])
def home():
    user = None

    # user_ip = request.remote_addr
    # user = user_ip in user_ip
    username = supabase.table("user_data").select("username").eq("username", username).execute().data[0]['username'] if user else None
    email = supabase.table("user_data").select("email").eq("email", email).execute().data[0]['email'] if user else None


    return render_template('index.html', username=username, email=email)

# this tool route
@app.route('/tool', methods=['GET', 'POST'])
def tool():
    encoded_image = None  # Yeh HTML ko pass hoga
    user = None

    # user_ip = request.remote_addr
    # user = user_ip in user_ip
    username = supabase.table("user_data").select("username").eq("username", username).execute().data[0]['username'] if user else None
    email = supabase.table("user_data").select("email").eq("email", email).execute().data[0]['email'] if user else None


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

            
    return render_template('tool.html', user_photo=encoded_image, username=username, email=email)



@app.route('/compressor', methods=['GET', 'POST'])
def compressor():
    encoded_image = None  # Yeh HTML ko pass hoga
    # user = None

    # user_ip = request.remote_addr
    # user = supabase.table("users").select("*").eq("user_ip", user_ip).single().execute()
    username = supabase.table("user_data").select("username").eq("username", username).execute()
    email = supabase.table("user_data").select("email").eq("email", email).execute()


    if request.method == 'POST':
        quality = request.form.get('quality')
        file = request.files.get('my_photo')
        format = request.form.get('format')

        img = Image.open(file.stream)

        buffer = io.BytesIO()
        img.save(buffer, format=format.upper() if format in ['png', 'jpg', 'webp', 'avif'] else 'PNG', quality=int(quality), optimize=True)
        b64_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Data URL format jo HTML ka <img> tag samajhta hai
        encoded_image = f"data:image/{format};base64,{b64_string}"

    return render_template('compressor.html', compressed_photo=encoded_image, username=username, email=email)


@app.route('/enhance', methods=['GET', 'POST'])
def enhance():
    encoded_image = None

    if request.method == 'POST':
        file = request.files.get('image_file')
        brightness = request.form.get('brightness')
        contrast = request.form.get('contrast')
        saturation = request.form.get('saturation')
        sharpness = request.form.get('sharpness')
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'png'

        # 1. Base Image Stream read karein
        img = Image.open(file.stream)

        # 2. Pura modification pipeline execute karke image object ko overwrite karein
        img = ImageEnhance.Brightness(img).enhance(float(brightness) / 100)
        img = ImageEnhance.Contrast(img).enhance(float(contrast) / 100)
        img = ImageEnhance.Color(img).enhance(float(saturation) / 100)
        img = ImageEnhance.Sharpness(img).enhance(float(sharpness) / 100)

        # 3. Format control target set karein
        save_format = 'JPEG' if ext in ['jpg', 'jpeg'] else 'PNG'
        
        # Cross-compatibility fix for alpha channel handling in JPEGs
        if img.mode in ('RGBA', 'LA') and save_format == 'JPEG':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background

        # 4. Ab buffer stream allocation clear run karein
        buffer = io.BytesIO()
        
        # FIX: Ab image pass karne ki jagah actual 'format' string dynamic update ho rahi hai
        img.save(buffer, format=save_format, optimize=True)
        
        b64_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
        encoded_image = f"data:image/{ext};base64,{b64_string}"

    return render_template('enhance.html', processed_image=encoded_image)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_name = supabase.table("user_data").select("username").eq("username", username).execute()
        user_pass = supabase.table("user_data").select("password").eq("password", password).execute()
        if username in user_name and password in user_pass:
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
        # user_ip = request.remote_addr
        check = supabase.table("user_data").select("email").eq("email", email).execute()
        if email not in check:
            try:
               data = {
                   "username": username,
                   "email": email,
                   "password": password,
                   "account_date": datetime.now(timezone.utc).isoformat()
               }
               
               response = supabase.table("user_data").insert(data).execute()
               print("Data inserted successfully:", response)
           
            except Exception as e:
                print("Error inserting data:", e)
            return redirect('/')
        else:
            return redirect(url_for('login'))
    
    return render_template('signup.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)