import pymysql


def get_connection(config):
    return pymysql.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        db=config["dbname"],
        charset="utf8"
    )
