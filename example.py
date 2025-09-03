from splunklib import client

service = client.connect(host="localhost", username="admin", password="changed!", autologin=True)

for app in service.apps:
    print(app.setupInfo)
