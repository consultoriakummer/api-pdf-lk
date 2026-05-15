from flask import Flask, request, jsonify, send_file
import io
from gerar_pdf import gerar_pdf_diagnostico

app = Flask(__name__)

@app.route("/gerar-pdf", methods=["POST"])
def gerar_pdf():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados não recebidos"}), 400
    pdf_bytes = gerar_pdf_diagnostico(dados)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="diagnostico.pdf"
    )

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "servico": "API PDF Luis Kummer"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
