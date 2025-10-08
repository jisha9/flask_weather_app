from dotenv import load_dotenv
load_dotenv()


from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import os

app = Flask(__name__)

# Database setup
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'weather.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
print("✅ Database path:", os.path.join(basedir, 'weather.db'))


# Database model
class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    temperature = db.Column(db.String(10))
    description = db.Column(db.String(50))

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# Replace this with your OpenWeatherMap API key
import os
API_KEY = os.getenv('WEATHER_API_KEY')


# Home route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city_name = request.form.get('city')
        if city_name:
            # Fetch weather data
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric"
            response = requests.get(url).json()
            
            if response.get('cod') == 200:
                temp = str(response['main']['temp'])
                desc = response['weather'][0]['description']
                
                # Save city if it doesn't already exist
                if not City.query.filter_by(name=city_name).first():
                    new_city = City(name=city_name, temperature=temp, description=desc)
                    db.session.add(new_city)
                    db.session.commit()
            
            return redirect(url_for('index'))
    
    # Get all cities from DB
    cities = City.query.all()
    return render_template('index.html', cities=cities)

# Delete city
@app.route('/delete/<int:id>')
def delete_city(id):
    city = City.query.get_or_404(id)
    db.session.delete(city)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
