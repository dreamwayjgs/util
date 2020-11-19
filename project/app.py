from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/position/update", methods=["PUT"])
def add_position():
    payload = request.json
    print(payload)
    # TODO: 들어온 데이터의 deviceid 파악: payload['data']['deviceid']
    # TODO: deviceid 별로 현재까지의 stop 검출
    # CASE1: deviceid 로 들어온 stop 후보 queue 가 없을 때
    # 새로운 stop stack 시작
    # CASE2: deviceid 로 이미 들어온 stop 후보 queue 가 있을 때
    # queue에 쌓인 데이터로 검출된 stop 과 queue + 새 위치로 검출한 stop 의 거리 차이를 계산
    # 임의의 거리 km 이상일 때
    # 좌표 - 거리 검출은 geopy의 distance 등을 사용 https://geopy.readthedocs.io/en/stable/#module-geopy.distance
    return "OK"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
