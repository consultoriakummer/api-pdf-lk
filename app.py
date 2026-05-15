from flask import Flask, request, jsonify
import base64
from gerar_pdf import gerar_pdf_diagnostico

app = Flask(__name__)

@app.route("/gerar-pdf", methods=["POST"])
def gerar_pdf():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados não recebidos"}), 400
    
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
