from flask import Flask, request, jsonify
import base64
from gerar_pdf import gerar_pdf_diagnostico

app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@app.route("/gerar-pdf", methods=["POST", "OPTIONS"])
def gerar_pdf():
    if request.method == "OPTIONS":
        return "", 204

    dados = request.get_json(force=True, silent=True)
    if not dados:
        return jsonify({
            "erro": "Dados não recebidos",
            "content_type": request.content_type,
            "body_raw": request.data.decode("utf-8")[:500]
        }), 400

    pdf_bytes = gerar_pdf_diagnostico(dados)
    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

    return jsonify({
        "status": "ok",
        "pdf_base64": pdf_base64,
        "nome": dados.get("nome", "aluno")
    })

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "servico": "API PDF Luis Kummer"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
