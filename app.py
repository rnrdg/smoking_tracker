import os
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from models import db, Cigarette, Settings

app = Flask(__name__)

# Config
db_path = os.environ.get("DB_NAME", "smoking_tracker.db")
# Ensure absolute path if not provided
if not os.path.isabs(db_path):
    db_path = os.path.join(app.root_path, db_path)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Ensure tables are created (important for Docker/Gunicorn)
with app.app_context():
    db.create_all()

def get_settings():
    settings = Settings.query.first()
    if not settings:
        settings = Settings(pack_price=700, pack_size=20)
        db.session.add(settings)
        db.session.commit()
    return settings

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/init', methods=['GET'])
def init_data():
    """Returns initial data: settings, today count, etc."""
    settings = get_settings()
    
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = Cigarette.query.filter(Cigarette.timestamp >= today_start).count()
    
    return jsonify({
        'settings': settings.to_dict(),
        'today_count': today_count
    })

@app.route('/api/log', methods=['POST'])
def log_cigarette():
    data = request.json or {}
    trigger = data.get('trigger', 'Other')
    
    settings = get_settings()
    single_cost = settings.pack_price / settings.pack_size if settings.pack_size > 0 else 0
    
    cig = Cigarette(trigger=trigger, cost=single_cost)
    db.session.add(cig)
    db.session.commit()
    
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = Cigarette.query.filter(Cigarette.timestamp >= today_start).count()
    
    return jsonify({'status': 'success', 'today_count': today_count})

@app.route('/api/undo', methods=['POST'])
def undo_cigarette():
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get last cigarette logged today
    last_cig = Cigarette.query.filter(Cigarette.timestamp >= today_start).order_by(Cigarette.id.desc()).first()
    
    if last_cig:
        db.session.delete(last_cig)
        db.session.commit()
        success = True
    else:
        success = False
        
    today_count = Cigarette.query.filter(Cigarette.timestamp >= today_start).count()
    return jsonify({'status': 'success' if success else 'failed', 'today_count': today_count})

@app.route('/api/settings', methods=['POST'])
def update_settings():
    data = request.json
    settings = get_settings()
    
    if 'pack_price' in data:
        settings.pack_price = int(data['pack_price'])
    if 'pack_size' in data:
        settings.pack_size = int(data['pack_size'])
        
    db.session.commit()
    return jsonify({'status': 'success', 'settings': settings.to_dict()})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    # 1. Money Spent
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = today_start.replace(day=1)
    
    today_cigs = Cigarette.query.filter(Cigarette.timestamp >= today_start).all()
    month_cigs = Cigarette.query.filter(Cigarette.timestamp >= month_start).all()
    
    spent_today = sum(c.cost for c in today_cigs)
    spent_month = sum(c.cost for c in month_cigs)
    
    # 2. Last 7 days chart data
    chart_labels = []
    chart_data = []
    
    for i in range(6, -1, -1):
        day = today_start - timedelta(days=i)
        next_day = day + timedelta(days=1)
        day_str = day.strftime('%d.%m')
        
        count = Cigarette.query.filter(
            Cigarette.timestamp >= day,
            Cigarette.timestamp < next_day
        ).count()
        
        chart_labels.append(day_str)
        chart_data.append(count)
        
    return jsonify({
        'money': {
            'today': round(spent_today, 2),
            'month': round(spent_month, 2)
        },
        'chart': {
            'labels': chart_labels,
            'data': chart_data
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
