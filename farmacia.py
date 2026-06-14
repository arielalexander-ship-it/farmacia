from flask import Flask, render_template_string, request, redirect
import psycopg2
import os

app = Flask(__name__)

def get_conn():
    return psycopg2.connect(os.environ['DATABASE_URL'])

def crear_base_datos():
    con = get_conn()
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS medicamentos (
        id SERIAL PRIMARY KEY,
        nombre TEXT NOT NULL,
        tipo TEXT NOT NULL,
        marca TEXT NOT NULL,
        caducidad TEXT NOT NULL,
        ubicacion TEXT NOT NULL
    )''')
    con.commit()
    cur.close()
    con.close()

def obtener_medicamentos():
    con = get_conn()
    cur = con.cursor()
    cur.execute('SELECT * FROM medicamentos')
    filas = cur.fetchall()
    cur.close()
    con.close()
    return filas

def agregar_medicamento(nombre, tipo, marca, caducidad, ubicacion):
    con = get_conn()
    cur = con.cursor()
    cur.execute('INSERT INTO medicamentos (nombre, tipo, marca, caducidad, ubicacion) VALUES (%s,%s,%s,%s,%s)',
                (nombre, tipo, marca, caducidad, ubicacion))
    con.commit()
    cur.close()
    con.close()

def eliminar_medicamento(id):
    con = get_conn()
    cur = con.cursor()
    cur.execute('DELETE FROM medicamentos WHERE id = %s', (id,))
    con.commit()
    cur.close()
    con.close()

TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Farmacia</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Segoe UI', sans-serif;
            min-height: 100vh;
            background: radial-gradient(ellipse at 40% 30%, #4a1d7a 0%, #1a0a2e 100%);
            position: relative;
            overflow-x: hidden;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background:
                radial-gradient(ellipse 120px 120px at 5% 18%, rgba(245,240,255,0.18) 0%, transparent 70%),
                radial-gradient(ellipse 100px 100px at 95% 18%, rgba(232,121,249,0.18) 0%, transparent 70%),
                radial-gradient(ellipse 80px 80px at 5% 88%, rgba(192,132,252,0.15) 0%, transparent 70%),
                radial-gradient(ellipse 80px 80px at 95% 88%, rgba(245,240,255,0.15) 0%, transparent 70%);
            pointer-events: none;
            z-index: 0;
        }

        header {
            background: rgba(255,255,255,0.10);
            backdrop-filter: blur(8px);
            color: white;
            padding: 22px 40px;
            display: flex;
            align-items: center;
            gap: 14px;
            border-bottom: 1px solid rgba(255,255,255,0.12);
            position: relative;
            z-index: 1;
        }

        header h1 { font-size: 26px; font-weight: 600; color: #f5f0ff; letter-spacing: 0.5px; }
        header span { font-size: 32px; }

        .container { max-width: 1200px; margin: 36px auto; padding: 0 24px; position: relative; z-index: 1; }

        .card {
            background: rgba(255,255,255,0.10);
            backdrop-filter: blur(6px);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 14px;
            padding: 28px;
            margin-bottom: 24px;
        }

        .card h2 {
            font-size: 12px;
            color: #e9d5ff;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            margin-bottom: 18px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }

        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px;
            align-items: end;
        }

        .form-group { display: flex; flex-direction: column; gap: 5px; }

        .form-group label {
            font-size: 11px;
            color: #c4b5fd;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        input {
            padding: 10px 14px;
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.18);
            border-radius: 8px;
            font-size: 14px;
            color: #f5f0ff;
            outline: none;
            transition: border 0.2s;
        }

        input::placeholder { color: rgba(196,181,253,0.6); }
        input:focus { border-color: #c084fc; background: rgba(255,255,255,0.14); }

        .btn {
            padding: 10px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: opacity 0.2s;
            height: 42px;
        }

        .btn-primary { background: #9333ea; color: white; }
        .btn-primary:hover { background: #7e22ce; }

        .btn-danger {
            background: rgba(124,58,237,0.5);
            color: #f3e8ff;
            border: 1px solid rgba(196,181,253,0.3);
            padding: 5px 12px;
            height: auto;
            font-size: 12px;
            border-radius: 6px;
        }

        .btn-danger:hover { background: rgba(124,58,237,0.8); }

        .search-bar { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; }
        .search-bar input { flex: 1; }

        .badge {
            background: rgba(147,51,234,0.4);
            color: #e9d5ff;
            font-size: 12px;
            font-weight: 700;
            padding: 4px 12px;
            border-radius: 20px;
            border: 1px solid rgba(196,181,253,0.3);
            white-space: nowrap;
        }

        table { width: 100%; border-collapse: collapse; font-size: 14px; }

        thead tr {
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }

        th {
            padding: 10px 14px;
            text-align: left;
            font-size: 11px;
            font-weight: 700;
            color: #c4b5fd;
            text-transform: uppercase;
            letter-spacing: 0.6px;
        }

        td { padding: 12px 14px; color: #f3e8ff; }

        tbody tr { border-bottom: 1px solid rgba(255,255,255,0.06); transition: background 0.15s; }
        tbody tr:hover { background: rgba(255,255,255,0.06); }

        .id-badge {
            background: rgba(147,51,234,0.4);
            color: #e9d5ff;
            font-weight: 700;
            padding: 3px 9px;
            border-radius: 6px;
            font-size: 12px;
        }

        .tipo-tag {
            background: rgba(245,240,255,0.12);
            color: #ddd6fe;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            border: 1px solid rgba(196,181,253,0.25);
        }

        .stats { display: flex; gap: 16px; margin-bottom: 24px; }

        .stat-card {
            flex: 1;
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 14px;
            padding: 20px 24px;
            border-top: 3px solid;
        }

        .stat-card:nth-child(1) { border-top-color: #f9a8d4; }
        .stat-card:nth-child(2) { border-top-color: #c4b5fd; }
        .stat-card:nth-child(3) { border-top-color: #f5f0ff; }

        .stat-card .number { font-size: 32px; font-weight: 700; color: #f5f0ff; }
        .stat-card .label { font-size: 13px; color: #c4b5fd; margin-top: 4px; }

        .no-results { text-align: center; padding: 40px; color: #c4b5fd; font-size: 15px; }

        /* Orquídeas SVG de fondo */
        .orquideas {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            pointer-events: none;
            z-index: 0;
        }
    </style>
</head>
<body>

<svg class="orquideas" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <!-- Orquídea blanca superior izquierda -->
  <g opacity="0.7">
    <ellipse cx="100" cy="130" rx="45" ry="22" fill="#f5f0ff" transform="rotate(-30 100 130)"/>
    <ellipse cx="65" cy="112" rx="36" ry="18" fill="#ede9fe" transform="rotate(20 65 112)"/>
    <ellipse cx="138" cy="105" rx="36" ry="18" fill="#ede9fe" transform="rotate(-20 138 105)"/>
    <ellipse cx="90" cy="88" rx="30" ry="15" fill="#f5f0ff" transform="rotate(10 90 88)"/>
    <ellipse cx="122" cy="148" rx="30" ry="15" fill="#f5f0ff" transform="rotate(-10 122 148)"/>
    <circle cx="101" cy="118" r="12" fill="#ffffff"/>
    <circle cx="101" cy="118" r="5" fill="#e9d5ff"/>
    <line x1="101" y1="130" x2="101" y2="220" stroke="#9f7aea" stroke-width="2"/>
    <ellipse cx="78" cy="210" rx="24" ry="10" fill="#6d28d9" opacity="0.35" transform="rotate(-15 78 210)"/>
    <ellipse cx="124" cy="195" rx="24" ry="10" fill="#6d28d9" opacity="0.35" transform="rotate(20 124 195)"/>
  </g>
  <!-- Orquídea morada superior derecha -->
  <g opacity="0.7">
    <ellipse cx="1340" cy="130" rx="45" ry="22" fill="#e879f9" transform="rotate(30 1340 130)"/>
    <ellipse cx="1375" cy="112" rx="36" ry="18" fill="#d946ef" transform="rotate(-20 1375 112)"/>
    <ellipse cx="1305" cy="105" rx="36" ry="18" fill="#d946ef" transform="rotate(20 1305 105)"/>
    <ellipse cx="1345" cy="88" rx="30" ry="15" fill="#e879f9" transform="rotate(-10 1345 88)"/>
    <ellipse cx="1318" cy="148" rx="30" ry="15" fill="#e879f9" transform="rotate(10 1318 148)"/>
    <circle cx="1338" cy="118" r="12" fill="#fdf4ff"/>
    <circle cx="1338" cy="118" r="5" fill="#f0abfc"/>
    <line x1="1338" y1="130" x2="1338" y2="220" stroke="#86198f" stroke-width="2"/>
    <ellipse cx="1360" cy="210" rx="24" ry="10" fill="#701a75" opacity="0.35" transform="rotate(15 1360 210)"/>
    <ellipse cx="1315" cy="195" rx="24" ry="10" fill="#701a75" opacity="0.35" transform="rotate(-20 1315 195)"/>
  </g>
  <!-- Orquídea blanca inferior derecha -->
  <g opacity="0.55">
    <ellipse cx="1350" cy="780" rx="40" ry="20" fill="#f5f0ff" transform="rotate(25 1350 780)"/>
    <ellipse cx="1315" cy="762" rx="32" ry="16" fill="#ede9fe" transform="rotate(-15 1315 762)"/>
    <ellipse cx="1385" cy="762" rx="32" ry="16" fill="#ede9fe" transform="rotate(15 1385 762)"/>
    <circle cx="1350" cy="772" r="10" fill="#ffffff"/>
    <circle cx="1350" cy="772" r="4" fill="#ddd6fe"/>
    <line x1="1350" y1="782" x2="1350" y2="860" stroke="#7c3aed" stroke-width="2"/>
    <ellipse cx="1328" cy="852" rx="20" ry="9" fill="#4c1d95" opacity="0.35" transform="rotate(-10 1328 852)"/>
  </g>
  <!-- Orquídea lila inferior izquierda -->
  <g opacity="0.55">
    <ellipse cx="90" cy="780" rx="40" ry="20" fill="#c084fc" transform="rotate(-25 90 780)"/>
    <ellipse cx="55" cy="762" rx="32" ry="16" fill="#a855f7" transform="rotate(15 55 762)"/>
    <ellipse cx="125" cy="762" rx="32" ry="16" fill="#a855f7" transform="rotate(-15 125 762)"/>
    <circle cx="90" cy="772" r="10" fill="#f3e8ff"/>
    <circle cx="90" cy="772" r="4" fill="#fdf4ff"/>
    <line x1="90" y1="782" x2="90" y2="860" stroke="#6d28d9" stroke-width="2"/>
    <ellipse cx="112" cy="852" rx="20" ry="9" fill="#4c1d95" opacity="0.35" transform="rotate(10 112 852)"/>
  </g>
  <!-- Florecitas pequeñas -->
  <circle cx="400" cy="50" r="5" fill="#f5f0ff" opacity="0.35"/>
  <circle cx="720" cy="30" r="4" fill="#e879f9" opacity="0.3"/>
  <circle cx="1050" cy="55" r="5" fill="#f5f0ff" opacity="0.3"/>
  <circle cx="250" cy="870" r="4" fill="#c084fc" opacity="0.3"/>
  <circle cx="650" cy="880" r="4" fill="#f5f0ff" opacity="0.3"/>
  <circle cx="1100" cy="865" r="4" fill="#e879f9" opacity="0.3"/>
</svg>

<header>
    <span>💊</span>
    <h1>Inventario Farmacia</h1>
</header>

<div class="container">
    <div class="stats">
        <div class="stat-card">
            <div class="number">{{ medicamentos|length }}</div>
            <div class="label">Medicamentos registrados</div>
        </div>
        <div class="stat-card">
            <div class="number">{{ medicamentos|map(attribute=2)|unique|list|length }}</div>
            <div class="label">Tipos distintos</div>
        </div>
        <div class="stat-card">
            <div class="number">{{ medicamentos|map(attribute=3)|unique|list|length }}</div>
            <div class="label">Marcas distintas</div>
        </div>
    </div>

    <div class="card">
        <h2>➕ Agregar medicamento</h2>
        <form method="POST" action="/agregar">
            <div class="form-grid">
                <div class="form-group">
                    <label>Nombre</label>
                    <input name="nombre" placeholder="Ej: Paracetamol" required>
                </div>
                <div class="form-group">
                    <label>Tipo</label>
                    <input name="tipo" placeholder="Ej: Analgésico" required>
                </div>
                <div class="form-group">
                    <label>Marca</label>
                    <input name="marca" placeholder="Ej: Genérico" required>
                </div>
                <div class="form-group">
                    <label>Caducidad</label>
                    <input name="caducidad" placeholder="MM/AAAA" required>
                </div>
                <div class="form-group">
                    <label>Ubicación</label>
                    <input name="ubicacion" placeholder="Ej: Estante A1" required>
                </div>
                <button type="submit" class="btn btn-primary">+ Agregar</button>
            </div>
        </form>
    </div>

    <div class="card">
        <h2>🔍 Buscar y ver inventario</h2>
        <div class="search-bar">
            <input type="text" id="buscador" placeholder="Buscar por nombre, tipo, marca o ubicación..." onkeyup="filtrar()">
            <span class="badge" id="conteo">{{ medicamentos|length }} resultados</span>
        </div>
        <table id="tabla">
            <thead>
                <tr>
                    <th>ID</th><th>Nombre</th><th>Tipo</th><th>Marca</th><th>Caducidad</th><th>Ubicación</th><th>Acción</th>
                </tr>
            </thead>
            <tbody id="cuerpo">
                {% for m in medicamentos %}
                <tr>
                    <td><span class="id-badge">{{ m[0] }}</span></td>
                    <td><strong>{{ m[1] }}</strong></td>
                    <td><span class="tipo-tag">{{ m[2] }}</span></td>
                    <td>{{ m[3] }}</td>
                    <td>{{ m[4] }}</td>
                    <td>{{ m[5] }}</td>
                    <td>
                        <form method="POST" action="/eliminar/{{ m[0] }}" onsubmit="return confirm('¿Eliminar {{ m[1] }}?')">
                            <button type="submit" class="btn btn-danger">🗑 Eliminar</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <div class="no-results" id="sinResultados" style="display:none;">No se encontraron resultados.</div>
    </div>
</div>

<script>
function filtrar() {
    const texto = document.getElementById('buscador').value.toLowerCase();
    const filas = document.querySelectorAll('#cuerpo tr');
    let visibles = 0;
    filas.forEach(fila => {
        const mostrar = fila.textContent.toLowerCase().includes(texto);
        fila.style.display = mostrar ? '' : 'none';
        if (mostrar) visibles++;
    });
    document.getElementById('conteo').textContent = visibles + ' resultados';
    document.getElementById('sinResultados').style.display = visibles === 0 ? 'block' : 'none';
}
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(TEMPLATE, medicamentos=obtener_medicamentos())

@app.route('/agregar', methods=['POST'])
def agregar():
    agregar_medicamento(
        request.form['nombre'],
        request.form['tipo'],
        request.form['marca'],
        request.form['caducidad'],
        request.form['ubicacion']
    )
    return redirect('/')

@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    eliminar_medicamento(id)
    return redirect('/')

crear_base_datos()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
