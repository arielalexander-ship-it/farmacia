from flask import Flask, render_template_string, request, redirect
import sqlite3

app = Flask(__name__)

def crear_base_datos():
    con = sqlite3.connect('farmacia.db')
    con.execute('''CREATE TABLE IF NOT EXISTS medicamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        tipo TEXT NOT NULL,
        marca TEXT NOT NULL,
        caducidad TEXT NOT NULL,
        ubicacion TEXT NOT NULL
    )''')
    con.commit()
    con.close()

def obtener_medicamentos():
    con = sqlite3.connect('farmacia.db')
    filas = con.execute('SELECT * FROM medicamentos').fetchall()
    con.close()
    return filas

def agregar_medicamento(nombre, tipo, marca, caducidad, ubicacion):
    con = sqlite3.connect('farmacia.db')
    con.execute('INSERT INTO medicamentos (nombre, tipo, marca, caducidad, ubicacion) VALUES (?,?,?,?,?)',
                (nombre, tipo, marca, caducidad, ubicacion))
    con.commit()
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
            background: #eef2f7;
            min-height: 100vh;
        }

        header {
            background: linear-gradient(135deg, #1a73e8, #0d47a1);
            color: white;
            padding: 24px 40px;
            display: flex;
            align-items: center;
            gap: 14px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        header h1 { font-size: 26px; font-weight: 600; letter-spacing: 0.5px; }
        header span { font-size: 32px; }

        .container { max-width: 1200px; margin: 36px auto; padding: 0 24px; }

        .card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            padding: 28px;
            margin-bottom: 28px;
        }

        .card h2 {
            font-size: 15px;
            color: #555;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 18px;
            border-bottom: 2px solid #eef2f7;
            padding-bottom: 10px;
        }

        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
            align-items: end;
        }

        .form-group { display: flex; flex-direction: column; gap: 5px; }

        .form-group label {
            font-size: 12px;
            color: #888;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        input {
            padding: 10px 14px;
            border: 1.5px solid #dde3ec;
            border-radius: 8px;
            font-size: 14px;
            color: #333;
            transition: border 0.2s;
            outline: none;
        }

        input:focus { border-color: #1a73e8; }

        button {
            padding: 10px 24px;
            background: linear-gradient(135deg, #1a73e8, #0d47a1);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: opacity 0.2s;
            height: 42px;
        }

        button:hover { opacity: 0.88; }

        .search-bar {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
        }

        .search-bar input {
            flex: 1;
            padding: 10px 16px;
            border-radius: 8px;
            border: 1.5px solid #dde3ec;
            font-size: 14px;
        }

        .badge {
            background: #e8f0fe;
            color: #1a73e8;
            font-size: 12px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 20px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }

        thead tr {
            background: #f4f7fb;
            color: #555;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.6px;
        }

        th, td { padding: 14px 16px; text-align: left; }

        th { font-weight: 700; color: #666; }

        tbody tr {
            border-top: 1px solid #f0f0f0;
            transition: background 0.15s;
        }

        tbody tr:hover { background: #f0f6ff; }

        .id-badge {
            background: #e8f0fe;
            color: #1a73e8;
            font-weight: 700;
            padding: 3px 9px;
            border-radius: 6px;
            font-size: 13px;
        }

        .tipo-tag {
            background: #e6f4ea;
            color: #2e7d32;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }

        .no-results {
            text-align: center;
            padding: 40px;
            color: #aaa;
            font-size: 15px;
        }

        .stats {
            display: flex;
            gap: 16px;
            margin-bottom: 28px;
        }

        .stat-card {
            flex: 1;
            background: white;
            border-radius: 12px;
            padding: 20px 24px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.07);
            border-left: 4px solid #1a73e8;
        }

        .stat-card .number { font-size: 32px; font-weight: 700; color: #1a73e8; }
        .stat-card .label { font-size: 13px; color: #888; margin-top: 4px; }
    </style>
</head>
<body>

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
        <div class="stat-card" style="border-left-color: #2e7d32;">
            <div class="number" style="color:#2e7d32;">{{ medicamentos|map(attribute=2)|unique|list|length }}</div>
            <div class="label">Tipos distintos</div>
        </div>
        <div class="stat-card" style="border-left-color: #f57c00;">
            <div class="number" style="color:#f57c00;">{{ medicamentos|map(attribute=3)|unique|list|length }}</div>
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
                <button type="submit">+ Agregar</button>
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
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Tipo</th>
                    <th>Marca</th>
                    <th>Caducidad</th>
                    <th>Ubicación</th>
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
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <div class="no-results" id="sinResultados" style="display:none;">
            No se encontraron resultados.
        </div>
    </div>

</div>

<script>
function filtrar() {
    const texto = document.getElementById('buscador').value.toLowerCase();
    const filas = document.querySelectorAll('#cuerpo tr');
    let visibles = 0;
    filas.forEach(fila => {
        const contenido = fila.textContent.toLowerCase();
        const mostrar = contenido.includes(texto);
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

crear_base_datos()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
