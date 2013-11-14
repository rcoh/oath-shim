from flask import Flask, render_template
app = Flask(__name__)

CLIENT_ID = "5fmnuoxq79novlted3hvo7jcc51a5zi6"
redirect_uri = "http://www.testapp.com:5001/"

@app.route('/')
def main():
    return render_template('app.html', redirect_uri = redirect_uri, client_id =
            CLIENT_ID)

if __name__ == '__main__':
    app.debug = True
    app.run(port = 5001)
