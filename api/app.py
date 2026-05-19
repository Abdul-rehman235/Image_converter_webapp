import base64, io

from flask import Flask, render_template, request, redirect, url_for, session
from PIL import Image


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def tool():
    encoded_image = None  # Yeh HTML ko pass hoga

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

            
    return render_template('tool.html', user_photo=encoded_image)





if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)