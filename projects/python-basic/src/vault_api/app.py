"""Flask API surface for vault-api."""

from flask import Flask, abort, jsonify, request

from . import auth, banking, db, files

app = Flask(__name__)


@app.post("/login")
def login():
    body = request.get_json(force=True)
    user = db.find_user_by_name(body["username"])
    if user and auth.verify_password(body["password"], user["password_hash"]):
        return jsonify({"token": auth.issue_token(user["id"])})
    abort(401)


@app.get("/account/<int:account_id>")
def account(account_id):
    acct = db.get_account(account_id)
    if acct is None:
        abort(404)
    return jsonify({"id": acct["id"], "balance": acct["balance"]})


@app.post("/transfer")
def do_transfer():
    body = request.get_json(force=True)
    new_balance = banking.transfer(body["from"], body["to"], body["amount"])
    return jsonify({"balance": new_balance})


@app.get("/files/<path:name>")
def download(name):
    data = files.read_user_file(name)
    return data


def main():
    db.init_db()
    app.run(host="127.0.0.1", port=5000)


if __name__ == "__main__":
    main()
